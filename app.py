import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse
from fastapi import Request

load_dotenv()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")

UPLOAD_FOLDER = "static/uploads"
GENERATED_FOLDER = "static/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

app.mount("/static", StaticFiles(directory='static'), name="static")

templates = Jinja2Templates(directory="templates")

from routes import router
app.include_router(router)

# @app.get("/routes")
# async def list_routes():
#     route_list = []
#     for r in app.router.routes:
#         if isinstance(r, APIRoute):  # only include real API routes
#             route_list.append({
#                 "path": r.path,
#                 "methods": list(r.methods)
#             })
#     return route_list


