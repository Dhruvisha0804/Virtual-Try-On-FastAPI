import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
from db_queries import insert_vto_tokens
from datetime import datetime
from pathlib import Path

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

product_image = Image.open('Kundan_set_new.jpg')

prompt = "A realistic photo of a human model or appropriate scene where the uploaded product is displayed or used naturally in the correct context."

image_response = model.generate_images(
    prompt=prompt,
    image=product_image
)

if image_response and image_response.images:
    output_img = image_response.images[0]

    UPLOAD_FOLDER = "static/generated"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    product_name = Path('Kundan_set_new.jpg').stem

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gen_img_name = f"{product_name}_genai_{timestamp}.png"
    output_path = os.path.join(UPLOAD_FOLDER, gen_img_name)

    output_img.save("generated_image.png")
    print("Image saved successfully.")

    print("\nFull metadata from GEMINI response:")
    print(image_response.__dict__)

    usage = getattr(image_response, "UsageMetadat", None)

    prompt_tokens = getattr(usage, "promptTokenCount", None)
    candidates_tokens = getattr(usage, "candidatesTokenCount", None)
    total_tokens = getattr(usage, "totalTokenCount", None)

    print("\nTokens Usage Stats:")
    print(f"\nInput Prompt Tokens: {prompt_tokens}")
    print(f"\nGenerated Image Tokens: {candidates_tokens}")
    print(f"\nTotal Tokens (prompt+response): {total_tokens}")

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
    print("No image generated.")