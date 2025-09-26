from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
from db_queries import insert_vto_tokens
from datetime import datetime
from pathlib import Path
import json

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


# Helper function to encode product image
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# # Correct path to your image
# product_image_path = "static/uploads/sky_blue_saree_new.jpg"
#
# # Safety check
# if not os.path.exists(product_image_path):
#     raise FileNotFoundError(f"File not found: {product_image_path}")
#
# # Encode image once
# product_image = encode_image(product_image_path)
#
# prompt = "A realistic photo of a human model or appropriate scene where the uploaded product is displayed or used naturally in the correct context."
#
# response = client.responses.create(
#     model="gpt-4.1",
#     input=[
#         {
#             "role": "user",
#             "content": [
#                 {"type": "input_text", "text": prompt},
#                 {
#                     "type": "input_image",
#                     "image_url": f"data:image/png;base64,{product_image}"
#                 }
#             ]
#         }
#     ],
#     tools=[{"type": "image_generation", "size": "1024x1024"}],
#     tool_choice={"type": "image_generation"}
# )
#
# # Print full API response
# print("\nFull API Response:")
# print(json.dumps(response.dict(), indent=2))
#
# # Extract image
# image_generation_calls = [
#     output for output in response.output if output.type == "image_generation_call"
# ]
#
# if not image_generation_calls:
#     print("No image generated.")
#     exit()
#
# tool_call_result_list = image_generation_calls[0].result
#
# if tool_call_result_list:
#     print("Image generation call completed but returned an empty result list.")
#     exit()
#
# image_base64 = tool_call_result_list[0]
#
# # image_base64 = image_generation_calls[0].result[0]
# # image_bytes = base64.b64decode(image_base64)
#
# # DEBUG STEP: Print the type and length of the variable BEFORE decoding.
# print(f"Type of image_base64: {type(image_base64)}")
# print(f"Length of image_base64: {len(image_base64) if isinstance(image_base64, str) else 'N/A'}")
#
# image_bytes = base64.b64decode(image_base64)
#
# UPLOAD_FOLDER = "static/generated"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#
# product_name = Path(product_image_path).stem
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# gen_img_name = f"{product_name}_genai_{timestamp}.png"
# output_path = os.path.join(UPLOAD_FOLDER, gen_img_name)
#
# with open(output_path, "wb") as f:
#     f.write(image_bytes)
#
# print(f"\nImage saved at: {output_path}")
#
# # Extract assistant text
# assistant_texts = [
#     content.text for output in response.output if hasattr(output, "content")
#     for content in output.content if content.type == "output_text"
# ]
# # assistant_text = "\n".join(assistant_texts)
# # print("\nAssistant Response:\n", assistant_text or "No text response.")
# assistant_text = response.output_text
# print("\nAssistant Response:\n", assistant_text or "No text response.")
#
# # Token usage
# usage = getattr(response, "usage", None)
# if usage:
#     print("\nTokens Usage Stats:")
#     print(f"Input Prompt Tokens: {usage.input_tokens}")
#     print(f"Generated Image Tokens: {usage.output_tokens}")
#     print(f"Total Tokens: {usage.total_tokens}")
# else:
#     print("\nToken usage not available for image generation.")
#
# # Insert tokens into DB
# success, msg = insert_vto_tokens(
#     prompt_tokens=getattr(usage, "input_tokens", 0),
#     input_img_tokens=1,
#     gen_img_name=gen_img_name,
#     gen_img_used_tokens=getattr(usage, "output_tokens", 0)
# )
#
# if success:
#     print("\nDB insert successful.")
# else:
#     print("\nDB insert error:", msg)


# Correct path to your image
product_image_path = "static/uploads/floral-pink-cordset.jpeg"

# Safety check
if not os.path.exists(product_image_path):
    raise FileNotFoundError(f"File not found: {product_image_path}")

# Encode image once
product_image = encode_image(product_image_path)
product_name = Path(product_image_path).stem

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

prompt = "A realistic photo of a human model or appropriate scene where the uploaded product is displayed or used naturally in the correct context."

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{product_image}"
                }
            ]
        }
    ],
    # tools=[{"type": "image_generation", "size": "1024x1024"}]
    tools=[{"type": "image_generation"}]
)

response_filename = f"full_api_response_{product_name}_{timestamp}.json"

with open(response_filename, "w", encoding="utf-8") as f:
    json.dump(response.dict(), f, indent=2, ensure_ascii=False)

print(f"✅ Full API response saved as {response_filename}.")


# Extract image
image_generation_calls = [
    output for output in response.output if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if not image_data:
    print("No image generated:", json.dumps(response.dict(), indent=2))
    exit()

image_base64 = image_data[0]
image_bytes = base64.b64decode(image_base64)

UPLOAD_FOLDER = "static/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

gen_img_name = f"{product_name}_genai_{timestamp}.png"
output_path = os.path.join(UPLOAD_FOLDER, gen_img_name)

with open(output_path, "wb") as f:
    f.write(image_bytes)

print(f"\nImage saved at: {output_path}")

# Extract assistant text
assistant_texts = [
    content.text for output in response.output if hasattr(output, "content")
    for content in output.content if content.type == "output_text"
]
assistant_text = response.output_text
print("\nAssistant Response:\n", assistant_text or "No text response.")

# Token usage
usage = getattr(response, "usage", None)
if usage:
    print("\nTokens Usage Stats:")
    print(f"Input Prompt Tokens: {usage.input_tokens}")
    print(f"Generated Image Tokens: {usage.output_tokens}")
    print(f"Total Tokens: {usage.total_tokens}")
else:
    print("\nToken usage not available for image generation.")

# # Insert tokens into DB
# success, msg = insert_vto_tokens(
#     prompt_tokens=getattr(usage, "input_tokens", 0),
#     input_img_tokens=1,
#     gen_img_name=gen_img_name,
#     gen_img_used_tokens=getattr(usage, "output_tokens", 0)
# )

# if success:
#     print("\nDB insert successful.")
# else:
#     print("\nDB insert error:", msg)
