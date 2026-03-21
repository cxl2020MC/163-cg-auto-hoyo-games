from pydantic import BaseModel
from enum import StrEnum
from pathlib import Path
from .log import logger as log


class GameEnum(StrEnum):
    jql_gjf = "jql_gjf"
    jql = "jql"

class _Account(BaseModel):
    username: str
    password: str
    id: str | None = None
    game: GameEnum = GameEnum.jql_gjf
    group_id: int | None = None


class _Config(BaseModel):
    image_change_dir: str = './img'
    data_dir: str = './data'
    push_token: str = ''
    push_url: str = ''
    accounts: list[_Account]


with open("./data/config.json", 'r', encoding='utf-8') as f:
    config = _Config.model_validate_json(f.read())
    log.debug(config)


CHANGE_IMG_DIR = Path(config.image_change_dir)

def get_img_file_path(file_name):
    return Path(CHANGE_IMG_DIR, file_name)


SCREENSHOT_PATH = get_img_file_path("screenshot.png")