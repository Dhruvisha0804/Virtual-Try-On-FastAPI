import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
from db_queries import insert_vto_tokens
from datetime import datetime
from pathlib import Path
import mimetypes
from extract_metadata import extract_response_info

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

from google import genai
from google.genai import types

client = genai.Client()

upload_path = "static/uploads/Totebag.jpg"

try:
    with open(upload_path, "rb") as img_file:
        image_bytes = img_file.read()
except FileNotFoundError:
    print(f"Error: Input file not found at {upload_path}.")
    exit()

mime_type, _ = mimetypes.guess_type(upload_path)
if not mime_type:
    mime_type = "image/jpeg"
    print(f"Warning: Could not detect MIME type, defaulting to {mime_type}")

product_image = types.Part.from_bytes(
    data=image_bytes,
    mime_type=mime_type
)

prompt = "A realistic photo of a human model or appropriate scene where the uploaded product is displayed or used naturally in the correct context."

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
    print("✅ Gemini response received")

    metadata = extract_response_info(response, prompt)

    print(f"**** {metadata}")

except Exception as e:
    print(f"Gemini API Call Error: {e}")
    exit()

# Extract generated image
if response and response.candidates and response.candidates[0].content.parts:
    output_img_bytes = None
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            print("Part MIME type:", part.inline_data.mime_type)
            print("Data length:", len(part.inline_data.data))
            print("First 50 chars:", part.inline_data.data[:50])

            try:
                # RAW bytes — no base64 decoding needed
                output_img_bytes = part.inline_data.data

                output_img = Image.open(BytesIO(output_img_bytes))
                output_img.load()  # Force load
                print("Image loaded successfully")
            except Exception as e:
                print(f"Error decoding image: {e}")

    if output_img_bytes:
        try:
            output_img = Image.open(BytesIO(output_img_bytes))

            UPLOAD_FOLDER = "static/generated"
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            product_name = Path(upload_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gen_img_name = f"{product_name}_genai_{timestamp}.png"
            output_path = os.path.join(UPLOAD_FOLDER, gen_img_name)

            output_img.save(output_path)
            print("Image saved successfully.", output_path)
        except Exception as e:
            print(f"Error saving or processing generated image: {e}")
            exit()

        # Tokens usage
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None)
        candidates_tokens = getattr(usage, "candidates_token_count", None)
        total_tokens = getattr(usage, "total_token_count", None)

        print("\nTokens Usage Stats:")
        print(f"Input Prompt Tokens: {prompt_tokens}")
        print(f"Generated Image Tokens: {candidates_tokens}")
        print(f"Total Tokens (prompt+response): {total_tokens}")

        success, msg = insert_vto_tokens(
            prompt_tokens=prompt_tokens,
            input_img_tokens=1,
            gen_img_name=gen_img_name,
            gen_img_used_tokens=candidates_tokens
        )

        if success:
            print("DB insert successfully.")
        else:
            print("DB insert error:", msg)

    else:
        text_output = getattr(response, "text", None)
        if text_output:
            print(f"⚠️ Model returned text, not an image. Text output: {text_output}")
        else:
            print("No image or text part generated.")

else:
    print("No image generated.")