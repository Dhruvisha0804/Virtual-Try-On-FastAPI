import json

with open("Full_Response_API_Call\\full_api_response_floral-pink-cordset_20250926_175026.json", encoding="utf-8") as f:
    json_data = json.load(f)

main_id = json_data["id"]

output1 = json_data["output"][0]
status_1 = output1["status"]
type_1 = output1["type"]
background_1 = output1["background"]
output_format_1 = output1["output_format"]
quality_1 = output1["quality"]
revised_prompt_1 = output1["revised_prompt"]
size_1 = output1["size"]

output2 = json_data["output"][1]
id_2 = output2["id"]
text_2 = output2["content"][0]["text"]
role_2 = output2["role"]
status_2 = output2["status"]
type_2 = output2["type"]

usage = json_data["usage"]
input_tokens = usage["input_tokens"]
output_tokens = usage["output_tokens"]
total_tokens = usage["total_tokens"]

print("Main ID:", main_id)
print("Output1:")
print(f"Status: {status_1}\nType: {type_1}\nBackground: {background_1}\nOutput_Format: {output_format_1}\nQuality: {quality_1}\n"
      f"Revised_prompt: {revised_prompt_1}\nSize: {size_1}")
print("Output2:")
print(f"Response_id: {id_2}\nText: {text_2}\nRole: {role_2}\nStatus: {status_2}\nType: {type_2}")
print("Usage:")
print(f"Input Tokens: {input_tokens}\nOutput Tokens: {output_tokens}\nTotal Tokens: {total_tokens}")



