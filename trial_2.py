# from fastapi import FastAPI, Form
# from fastapi.responses import JSONResponse
#
# app = FastAPI()
#
#
# @app.post("/test-login")
# async def test_login(user_id: str = Form(...), username: str = Form(...)):
#     return JSONResponse({
#         "message": "Login data received!",
#         "user_id": user_id,
#         "username": username
#     })

# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
#
# load_dotenv()
#
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# genai.configure(api_key=GEMINI_API_KEY)
#
# try:
#     model = genai.GenerativeModel("gemini-2.5-flash")
#     response = model.generate_content("Hello, Gemini!")
#     print("✅ Gemini API Key is valid.")
#     print("Response:", response.text)
# except Exception as e:
#     print("❌ API Key test failed:", e)


from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}