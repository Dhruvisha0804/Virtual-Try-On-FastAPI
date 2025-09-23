from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/test-login")
async def test_login(user_id: str = Form(...), username: str = Form(...)):
    return JSONResponse({
        "message": "Login data received!",
        "user_id": user_id,
        "username": username
    })
