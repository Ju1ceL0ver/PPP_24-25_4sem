from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.api.endpoints import router

app = FastAPI()
app.include_router(router)

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Корневой маршрут для главной страницы
from fastapi.responses import HTMLResponse
from fastapi import Request

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})