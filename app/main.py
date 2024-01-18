from aiohttp import web
from config import settings, logger, setup_logger
import logging
from app import create_app

logging.basicConfig(level=logging.DEBUG)
setup_logger()

app = create_app()
web.run_app(app)

