from io import BytesIO
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import google.generativeai as genai
from google.genai import types
# from google import genai
# from google.genai.types import GenerateContentConfig, Modality
import os
from pydantic import BaseModel
import logging

from database import get_db
from db_queries import insert_vto_tokens
from prompts import universal_prompt

# Configure Gemini once
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

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
async def upload_product(request: Request, file: UploadFile = File(...), db=Depends(get_db)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed.")

    try:
        filename = secure_filename(file.filename)
        upload_path = os.path.join("static/uploads", filename)

        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())

        req_received_time = datetime.now()

        product_image = Image.open(upload_path)
        prompt = request.session.get("last_prompt", universal_prompt)
        # request.session['last_prompt'] = prompt
        #
        # image_response = model.generate_images(prompt=prompt, image=product_image)

        # if image_response and image_response.images:
        #     output_img = image_response.images[0]
        #

        # Create a GenerateContentConfig instance
        generation_config_dict = {
            "response_modalities": [types.Modality.TEXT, types.Modality.IMAGE],
            "candidate_count": 1
        }

        # Generate content using the extracted parameters
        response = model.generate_content(
            contents=[prompt, product_image],
            generation_config=generation_config_dict
        )

        if response and response.candidates and response.candidates[0].content.parts:
            # Process the response as before
            output_img_bytes = None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    output_img_bytes = part.inline_data.data
                    break

            if output_img_bytes:
                output_img = Image.open(BytesIO(output_img_bytes))

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                product_base = os.path.splitext(filename)[0]
                gen_img_name = f"{product_base}_genai_{timestamp}.png"
                output_path = os.path.join("static/generated", gen_img_name)
                output_img.save(output_path)

            usage = getattr(response, "UsageMetadata", None)
            prompt_tokens = getattr(response, "promptTokenCount", None)
            candidates_tokens = getattr(response, "candidatesTokenCount", None)

            res_generated_time = datetime.now()

            success, msg = insert_vto_tokens(
                conn=db,
                user_id=request.session.get("user_id"),
                username=request.session.get("username"),
                req_received_time=req_received_time,
                res_generated_time=res_generated_time,
                prompt_tokens=prompt_tokens,
                input_img_tokens=1,
                gen_img_name=gen_img_name,
                gen_img_used_tokens=candidates_tokens,
            )

            return JSONResponse({
                "generated_img": f"/static/generated/{gen_img_name}",
                "prompt": prompt,
                "prompt_tokens": prompt_tokens,
                "generated_tokens": candidates_tokens,
                "message": "Generated successfully." if success else f"Generated but DB error: {msg}"
            })

        raise HTTPException(status_code=500, detail="AI did not generate image.")

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


