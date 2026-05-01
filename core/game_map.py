from enum import StrEnum

from . import config
from .log import logger as log


class GameIdEnum(StrEnum):
    JQL_GJF = "jql_gjf"
    JQL = "jql"
    BHXQTD_GJF = "bhxqtd_gjf"

class GameIdNotFoundError(Exception):
    pass

def get_game_id(game: config.GameEnum, server: config.GameServerEnum):
    game_id_map = {
        (config.GameEnum.jql, config.GameServerEnum.os): GameIdEnum.JQL_GJF,
        (config.GameEnum.jql, config.GameServerEnum.cn): GameIdEnum.JQL,
        (config.GameEnum.hsr, config.GameServerEnum.os): GameIdEnum.BHXQTD_GJF,

    }
    game_id = game_id_map.get((game, server), None)
    if game_id is None:
        raise GameIdNotFoundError(f"未找到游戏ID，游戏: {game}, 服务器: {server}")
    log.info(f"根据游戏 {game} 和服务器 {server} 获取到游戏ID: {game_id}")
    return game_id

def get_game_id_by_account(account: config._GameAccount):
    return get_game_id(account.game, account.server)