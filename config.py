'''
插件相关配置
Plugin configs
'''
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    update_time: int = 60 # 更新时间间隔 [分钟]
    update_notifiy: bool = True # 自动更新通知
    broadcast_hour: int = 8 # 播报今日比赛时间 [小时]
    broadcast_minute: int = 1 # 播报今日比赛时间 [分钟]