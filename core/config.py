from pydantic import BaseModel
from pathlib import Path
from .log import logger as log


class _Account(BaseModel):
    username: str
    password: str


class _Config(BaseModel):
    image_change_dir: str = './img'
    data_dir: str = './data'
    accounts: dict[str, _Account]


with open("./data/config.json", 'r', encoding='utf-8') as f:
    config = _Config.model_validate_json(f.read())
    log.debug(config)


CHANGE_IMG_DIR = config.image_change_dir

img_file_path = Path(CHANGE_IMG_DIR)

SCREENSHOT_PATH = img_file_path / "screenshot.png"
