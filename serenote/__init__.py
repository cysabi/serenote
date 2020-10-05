"""
Initalizes the early stuff for the entire application

This includes:
 - Initializing logging
"""

import os
import logging

debug = os.getenv("DEBUG")

# Initialize logging
logging.basicConfig(
    level=(
        logging.DEBUG if debug else logging.INFO
    ),
    format='%(levelname)s in %(filename)s on %(asctime)s: %(message)s',
    datefmt='%m/%d/%Y at %H:%M:%S'
)
logging.getLogger("discord").setLevel(logging.ERROR)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logging.getLogger(__name__)

if debug:
    logging.info(".env - 'DEBUG' key found. Running in debug mode, do not use in production.")
