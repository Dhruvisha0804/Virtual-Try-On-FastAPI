from db_queries import insert_vto_tokens
class MockUsageMetadata:
    def __init__(self, prompt, generated):
        self.promptTokenCount = prompt
        self.candidatesTokenCount = generated
        self.totalTokenCount = prompt + generated

# simulate usage with 150 prompt tokens and 300 generated tokens
mock_usage = MockUsageMetadata(prompt=150, generated=300)

print("Prompt tokens:", mock_usage.promptTokenCount)
print("Generated tokens:", mock_usage.candidatesTokenCount)
print("Total tokens:", mock_usage.totalTokenCount)

success, msg = insert_vto_tokens(
    prompt_tokens=mock_usage.promptTokenCount,
    input_img_tokens=1,
    gen_img_name="Kundan_set_new.jpg",
    gen_img_used_tokens=mock_usage.candidatesTokenCount
)

print(success, msg)
