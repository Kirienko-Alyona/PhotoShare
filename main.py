import pathlib
import time
#from ipaddress import ip_address
#from typing import Callable
import uvicorn
import redis.asyncio as redis

from fastapi import Depends, FastAPI, HTTPException, Request#, status
from fastapi.responses import HTMLResponse#, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
#from starlette.middleware.authentication import AuthenticationMiddleware

from src.database.db import get_db#, client_redis_for_main
from src.routes import photos, auth, users, comments, tags, photo_transformations, rates, photo_filters

from src.conf.config import settings


app = FastAPI()
favicon_path = 'static/images/favicon.ico'


@app.on_event("startup")
async def startup():
    
    redis_cache = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis_cache)
    
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)    
   
    
# ALLOWED_IPS = [ip_address("127.0.0.1"), ip_address("172.20.240.1"), ip_address('192.168.0.0'), ip_address('172.16.0.0')]


# @app.middleware("http")
# async def limit_access_by_ip(request: Request, call_next: Callable):
#     """
#     The limit_access_by_ip function is a middleware function that limits access to the API by IP address.
#     It checks if the client's IP address is in ALLOWED_IPS, and if not, returns a 403 Forbidden response.
    
#     :param request: Request: Get the ip address of the client that is making a request
#     :param call_next: Callable: Pass the next function in the chain to be executed
#     :return: A jsonresponse object if the client ip address is not in allowed_ips
#     """
#     ip = ip_address(request.client.host)
#     if ip not in ALLOWED_IPS:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
#     response = await call_next(request)
#     return response


@app.middleware('http')
async def custom_middleware(request: Request, call_next):
    """
    The custom_middleware function is a middleware function that adds the time it took to process the request
    to the response headers. This can be used for performance monitoring.
    
    :param request: Request: Get the request object
    :param call_next: Call the next middleware in the chain
    :return: A response object
    """
    start_time = time.time()
    response = await call_next(request)
    during = time.time() - start_time
    response.headers['performance'] = str(during)
    return response

templates = Jinja2Templates(directory='templates')
BASE_DIR = pathlib.Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """
    The favicon function returns the favicon.ico file from the static directory.
    
    :return: A file response with the contents of the favicon
    """
    return FileResponse(favicon_path)


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    """
    The root function is the entry point for the web application.
    It returns a TemplateResponse object, which renders an HTML template using Jinja2.
    The template is located in templates/index.html and uses data from the request object to render itself.
    
    :param request: Request: Get the request object
    :return: A templateresponse object
    """
    return templates.TemplateResponse('index.html', {"request": request, "title": "PhotoShare App"})


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is used to check the health of the database.
    It will return a 200 status code if it can successfully connect to the database,
    and a 500 status code otherwise.
    
    :param db: Session: Get the database session
    :return: A dictionary with a message
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(photos.router, prefix='/api')
app.include_router(photo_transformations.router, prefix='/api')
app.include_router(photo_filters.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(tags.router, prefix='/api')
app.include_router(rates.router, prefix='/api')



if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
    