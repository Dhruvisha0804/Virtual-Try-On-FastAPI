from io import BytesIO
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import google.generativeai as genai
import os
from pydantic import BaseModel
import logging
import mimetypes
import json

from database import get_db
from db_queries import insert_vto_tokens
from prompts import universal_prompt
from extract_metadata import extract_response_info

# Configure Gemini once
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-2.5-flash")
# model = genai.GenerativeModel("gemini-2.5-flash-image-preview")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

router = APIRouter()
templates = Jinja2Templates(directory='templates')

from google import genai
from google.genai import types

client = genai.Client()


class FeedbackRequest(BaseModel):
    note: str


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.get("/")
async def root():
    return RedirectResponse(url="/account")


@router.get("/account", response_class=HTMLResponse)
async def show_account_form(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})


@router.post("/account/login", response_class=HTMLResponse)
async def account_login(request: Request, user_id: str = Form(...), username: str = Form(...)):
    # Save session
    # print("user_id:", user_id)
    # print("username:", username)
    logging.info(f"user_id={user_id}, username={username}")
    request.session['user_id'] = user_id
    request.session['username'] = username

    # Redirect to index
    return RedirectResponse(url='/index', status_code=303)

@router.get("/index", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post('/index', response_class=HTMLResponse)
async def upload_product(request: Request,
                         file: UploadFile = File(...),
                         revised_prompt: str = Form(None),
                         db=Depends(get_db)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed.")

    try:
        filename = secure_filename(file.filename)
        upload_path = os.path.join("static/uploads", filename)

        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())

        req_received_time = datetime.now()
        # prompt = request.session.get("last_prompt", universal_prompt)
        request.session['last_prompt'] = None
        request.session['revised_prompt'] = None
        # prompt = revised_prompt or universal_prompt
        if revised_prompt:
            prompt = f"{universal_prompt}, {revised_prompt}"
        else:
            prompt = universal_prompt


        with open(upload_path, "rb") as img_file:
            image_bytes = img_file.read()

        mime_type, _ = mimetypes.guess_type(upload_path)
        if not mime_type:
            mime_type = "image/jpeg"

        product_image = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        generation_config_dict = {
            "candidate_count": 1
        }

        print("📌 Sending request to Gemini...")
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt, product_image],
                config=generation_config_dict
            )
        except Exception as gem_error:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {gem_error}")

        print("✅ Gemini response received")

        # print("FULL GEMINI RESPONSE:", response)

        print("Response ID:", getattr(response, "response_id", None))
        print("Model version:", getattr(response, "model_version", None))
        print("Prompt token count:", getattr(response.usage_metadata, "prompt_token_count", None))
        print("Candidates:", getattr(response, "candidates", None))

        for i, candidate in enumerate(response.candidates or []):
            print(f"Candidate {i} finish_reason:", candidate.finish_reason)
            print("Content role:", getattr(candidate.content, "role", None))
            print("Content parts:", getattr(candidate.content, "parts", None))


        try:
            metadata = extract_response_info(response, prompt)
        except Exception as meta_error:
            raise HTTPException(status_code=500, detail=f"Metadata extraction error: {meta_error}")

        if not (response.candidates and getattr(response.candidates[0].content, "parts", None)):
            print("⚠️ Gemini returned no usable content:", response)
            raise HTTPException(status_code=500, detail="AI did not generate usable content")

        try:
            output_img_bytes = None
            for part in response.candidates[0].content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    output_img_bytes = part.inline_data.data
                    break

            if not output_img_bytes:
                raise HTTPException(status_code=500, detail="No image bytes found in response")

            output_img = Image.open(BytesIO(output_img_bytes))
            output_img.load()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            product_base = os.path.splitext(filename)[0]
            gen_img_name = f"{product_base}_genai_{timestamp}.png"
            output_path = os.path.join("static/generated", gen_img_name)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            output_img.save(output_path)

        except Exception as img_error:
            raise HTTPException(status_code=500, detail=f"Image processing error: {img_error}")

        try:
            usage = response.usage_metadata
            text_tokens, image_tokens = 0, 0

            if getattr(usage, "prompt_tokens_details", None):
                for detail in usage.prompt_tokens_details:
                    if getattr(detail, "modality", "").upper() == "TEXT":
                        text_tokens = getattr(detail, "token_count", 0)
                    elif getattr(detail, "modality", "").upper() == "IMAGE":
                        image_tokens = getattr(detail, "token_count", 0)

            res_generated_time = datetime.now()
            # revised_prompt = request.session.get("revised_prompt", None)

            success, msg = insert_vto_tokens(
                conn=db,
                user_id=request.session.get("user_id"),
                username=request.session.get("username"),
                req_received_time=req_received_time,
                res_generated_time=res_generated_time,
                response_id=metadata["responseId"],
                input_prompt=metadata["inputPrompt"],
                text_tokens=metadata["usage"]["textTokens"],
                image_tokens=metadata["usage"]["imageTokens"],
                prompt_tokens_total=metadata["usage"]["promptTokensTotal"],
                revised_prompt=revised_prompt,
                candidates_tokens=metadata["usage"]["candidatesTokens"],
                output_texts="\n".join(metadata.get("outputTexts", [])),
                gen_img_name=gen_img_name
            )

        except Exception as db_error:
            raise HTTPException(status_code=500, detail=f"Database insert error: {db_error}")

        return JSONResponse({
            "generated_img": f"/static/generated/{gen_img_name}",
            "metadata": metadata,
            "prompt": prompt,
            "message": "Generated Successfully." if success else f"Generated but DB error: {msg}"
        })

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/feedback")
async def feedback(payload: FeedbackRequest, request: Request):
    try:
        note = payload.note.strip()

        if not note:
            return JSONResponse({"success": False, "error": "Feedback note is empty"}, status_code=400)

        new_prompt = f"{universal_prompt}, {note}"

        return {
            "success": True,
            "new_prompt": new_prompt,
            "note": note  # 👈 frontend can reuse this
        }

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)