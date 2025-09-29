import mimetypes
from io import BytesIO
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
from openai import OpenAI
import os
from pydantic import BaseModel
import logging
import base64
import mimetypes

from openai_database import get_db
from openai_db_queries import insert_vto_tokens_openai
from openai_prompt import universal_prompt


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

router = APIRouter()
templates = Jinja2Templates(directory='templates')


class FeedbackRequest(BaseModel):
    note: str


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.get("/account", response_class=HTMLResponse)
async def show_account_form(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})


@router.get("/index", response_class=HTMLResponse)
async def index_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/account/login", response_class=HTMLResponse)
async def account_login(request: Request, user_id: str = Form(...), username: str = Form(...)):
    # Save session
    print("user_id:", user_id)
    print("username:", username)
    logging.info(f"user_id={user_id}, username={username}")
    request.session['user_id'] = user_id
    request.session['username'] = username

    # Redirect to index
    return RedirectResponse(url='/index', status_code=303)


@router.post('/index', response_class=HTMLResponse)
async def upload_product_openai(request: Request, file: UploadFile = File(...), db=Depends(get_db)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed.")

    try:
        filename = secure_filename(file.filename)
        upload_path = os.path.join("static/uploads", filename)

        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())

        req_received_time = datetime.now()

        with open(upload_path, "rb") as img_file:
            image_bytes = img_file.read()

        mime_type, _ = mimetypes.guess_type(upload_path)
        if not mime_type:
            mime_type = "image/jpeg"

        img_base64 = base64.b64encode(image_bytes).decode("utf-8")
        image_data_uri = f"data:{mime_type};base64,{img_base64}"

        prompt = request.session.get("last_prompt", universal_prompt)
        approx_input_text_tokens = len(prompt) // 4

        # # Estimate 1 token = 4 characters. Add ~10 % buffer for complexity.
        # approx_input_text_tokens = int(len(prompt) / 4 * 1.1)

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": image_data_uri,
                        }
                    ],
                }
            ],
            tools=[{"type": "image_generation", "size": "auto"}]
        )

        response_dict = response.dict()

        # --- Extract fields ---
        main_id = response_dict.get("id", "")
        output1 = response_dict["output"][0]
        status_1 = output1.get("status", "")
        type_1 = output1.get("type", "")
        background = output1.get("background", "")
        output_format = output1.get("output_format", "")
        quality = output1.get("quality", "")
        revised_prompt = output1.get("revised_prompt", "")
        gen_img_size = output1.get("size", "")

        output2 = response_dict["output"][1]
        resp_id = output2.get("id", "")
        resp_text = output2["content"][0].get("text", "")
        role = output2.get("role", "")
        status_2 = output2.get("status", "")
        type_2 = output2.get("type", "")

        usage = response_dict.get("usage", {})
        input_total_tokens = usage.get("input_tokens", 0)
        output_text_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        # --- Save generated image ---
        output_img_bytes = base64.b64decode(output1.get("result", ""))
        output_img = Image.open(BytesIO(output_img_bytes))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        product_base = os.path.splitext(filename)[0]
        gen_img_name = f"{product_base}_openai_{timestamp}.png"
        output_path = os.path.join("static/generated", gen_img_name)
        output_img.save(output_path)

        res_generated_time = datetime.now()

        # --- Insert into DB ---
        success, msg = insert_vto_tokens_openai(
            conn=db,
            user_id=request.session.get("user_id"),
            username=request.session.get("username"),
            main_id=main_id,
            input_prompt=prompt,
            input_text_prompt_tokens=approx_input_text_tokens,
            output_format=output_format,
            quality=quality,
            revised_prompt=revised_prompt,
            gen_img_size=gen_img_size,
            resp_id=resp_id,
            resp_text=resp_text,
            input_total_tokens=input_total_tokens,
            output_text_tokens=output_text_tokens,
            total_tokens=total_tokens,
            req_received_time=req_received_time,
            res_generated_time=res_generated_time
        )

        return JSONResponse({
            "generated_img": f"/static/generated/{gen_img_name}",
            "prompt": prompt,
            "revised_prompt": revised_prompt,
            "status": status_1,
            "output_format": output_format,
            "quality": quality,
            "gen_img_size": gen_img_size,
            "resp_text": resp_text,
            "input_total_tokens": input_total_tokens,
            "output_text_tokens": output_text_tokens,
            "total_tokens": total_tokens,
            "message": "Generated successfully." if success else f"Generated but DB error: {msg}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/feedback")
async def feedback(payload: FeedbackRequest, request: Request):
    try:
        note = payload.note.strip()

        if not note:
            return JSONResponse({"success": False, "error": "Feedback note is empty"}, status_code=400)

        new_prompt = f"{universal_prompt}, {note}"
        request.session['last_prompt'] = new_prompt

        return {"success": True, "new_prompt": new_prompt}

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)