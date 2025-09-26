from openai import OpenAI
import base64
from dotenv import load_dotenv
import os

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
# resp = client.responses.create(
#     model="gpt-4.1-mini",
#     input="Hello from test!"
# )
#
# print(resp.output[0].content[0].text)




#
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
#
# response = client.responses.create(
#     model="gpt-5",
#     input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
#     tools=[{"type": "image_generation"}],
# )
#
# image_data = [
#     output.result
#     for output in response.output
#     if output.type == "image_generation_call"
# ]
#
# if image_data:
#     image_base64 = image_data[0]
#
#     with open("cat_and_otter.png", "wb") as f:
#         f.write(base64.b64decode(image_base64))
#
#
# # Follow up
#
# response_fwup = client.responses.create(
#     model="gpt-5",
#     previous_response_id=response.id,
#     input="Now make it look realistic",
#     tools=[{"type": "image_generation"}],
# )
#
# image_data_fwup = [
#     output.result
#     for output in response_fwup.output
#     if output.type == "image_generation_call"
# ]
#
# if image_data_fwup:
#     image_base64 = image_data_fwup[0]
#     with open("cat_and_otter_realistic.png", "wb") as f:
#         f.write(base64.b64decode(image_base64))




client = OpenAI()

# Helper function to encode product image
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Example: product image
product_image = encode_image("static/uploads/sky_blue_saree_new.jpg")

# Your text instruction
prompt = "A realistic photo of a human model or appropriate scene where the uploaded product is displayed or used naturally in the correct context."

# Call Responses API with tool = image_generation
response = client.responses.create(
    model="gpt-4.1",   # text model (it routes to image tool when tool is set)
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{product_image}",
                }
            ],
        }
    ],
    tools=[{"type": "image_generation",
            "size": "1024x1024"}]
)

# Extract generated image(s)
image_generation_calls = [
    output for output in response.output if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

# Save the first image
if image_data:
    image_base64 = image_data[0]
    with open("Generated_sky_blue_saree_new.jpg", "wb") as f:
        f.write(base64.b64decode(image_base64))
    print("✅ Image saved as output.png")
else:
    print("No image generated:", response.output)
