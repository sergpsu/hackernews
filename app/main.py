from aiohttp import web
from config import setup_logger
from app import create_app

setup_logger()

app = create_app()
web.run_app(app)
