| Resolution | Price per image |
| ---------- | --------------- |
| 256×256    | $0.016          |
| 512×512    | $0.018          |
| 1024×1024  | $0.020          |


Approx image tokens: https://platform.openai.com/docs/guides/images-vision?api-mode=responses

For GPT‑4.1:
Cost -> $0.002 / 1000 tokens

| Detail Level | Base Tokens                                                                    | Tile Tokens |
| ------------ |--------------------------------------------------------------------------------|-------------|
| High         | 85                                                                             | 170         |
| Medium/Low   | We'll treat Medium as same formula but with smaller token cost — often half)   |             |

Base tokens = 85
Tile tokens = 170


Generation Payload: {
  "imageData": {"url", "name"}, "Type": url/blob
  "prompt": "ghuitfrg",
  "background": "studio",
  "dimension": "1:1",
  "model": "female",
  "format": "jpeg",
  "age": "Young Adult",
  "tone": "Tan"
}

