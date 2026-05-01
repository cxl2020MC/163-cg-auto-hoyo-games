import tomllib
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel

from .log import logger as log


class GameEnum(StrEnum):
    jql = "jql"
    hsr = "hsr"


class GameServerEnum(StrEnum):
    cn = "cn"
    os = "os"
    bilibili = "bilibili"


class _GameAccount(BaseModel):
    id: str
    game: GameEnum = GameEnum.jql
    server: GameServerEnum = GameServerEnum.cn
    group_id: int | None = None


class _Config(BaseModel):
    image_change_dir: str = './img'
    data_dir: str = './data'
    push_token: str = ''
    push_url: str = ''
    game_accounts: list[_GameAccount]


# with open("./data/config.json", 'r', encoding='utf-8') as f:
#     config = _Config.model_validate_json(f.read())
#     log.debug(config)

with open("./data/config.toml", 'rb') as f:
    # config = _Config.model_validate_json(f.read())
    config = _Config.model_validate(tomllib.load(f))
    log.debug(config)

CHANGE_IMG_DIR = Path(config.image_change_dir)


def get_img_file_path(file_name):
    return Path(CHANGE_IMG_DIR, file_name)


SCREENSHOT_PATH = get_img_file_path("screenshot.png")
