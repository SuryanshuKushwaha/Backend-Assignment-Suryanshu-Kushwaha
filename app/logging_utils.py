import json
import logging
from datetime import datetime

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def log(data: dict):
    data["ts"] = datetime.utcnow().isoformat() + "Z"
    logger.info(json.dumps(data))
