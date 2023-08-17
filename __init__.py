from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.plugin import on_command, PluginMetadata, on_keyword
from nonebot import get_driver, logger, require
import nonebot
from datetime import datetime
from typing import List
import time
from os import makedirs, path

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .utils import upd_luogu, upd_cf, upd_atc, upd_nowcoder, get_today, get_preluogu, get_luogu, get_precf, get_cf, get_preatc, get_atc, get_prenc, get_nc

driver = get_driver()
global_config = get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = PluginMetadata(
    name="OCN",
    description="OI Contest Notifier订阅洛谷/CF/Atcoder/牛客平台的比赛信息",
    usage="luogu/preluogu(洛谷/洛谷历史) x 查询洛谷近期/历史的x场比赛（x默认为3）"
    "cf/precf x 查询CF近期/历史的x场比赛（x默认为3）"
    "atc/preatc x 查询Atcoder近期/历史的x场比赛（x默认为3）"
    "nc/prenc(牛客/牛客历史) x 查询牛客近期/历史的x场比赛（x默认为3）"
    "today(今日/今日比赛/今天/今天比赛) 查询所有平台今天的比赛"
    "next(近期/近期比赛) x 查询所有平台近期的x场比赛（x默认为3）"
    "update(手动更新) 手动更新缓存"
    "help 输出指令帮助")

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


@driver.on_startup
async def startup():
    # check data folder
    if not path.exists('data'):
        makedirs('./data')
    logger.info("自检成功！")


async def _update():
    await upd_luogu()
    await upd_cf()
    await upd_atc()
    await upd_nowcoder()


# 先写定时部分
# 定时自动更新缓存
#! 定时自动更新通知会向所有在.env.dev文件中配置了SUPERUSER的QQ号播报，config.py里有开关，默认开
@scheduler.scheduled_job('interval',
                         minutes=config.update_time,
                         id="auto_update")
async def auto_update():
    try:
        await _update()
        logger.info("自动更新成功！")
        if config.update_notifiy == True:
            # 轮番给管理发送更新成功消息
            for adid in global_config.superusers:
                await bot.send_msg(message_type="private",
                                   message="定时更新成功！\n" + "\n\n防风控编码" +
                                   str(time.time()),
                                   user_id=int(adid))
    except Exception as e:
        bot = nonebot.get_bot()
        logger.warning("自动更新失败！")
        logger.warning(e)
        if config.update_notifiy == True:
            # 轮番给管理发送更新失败消息
            for adid in global_config.superusers:
                await bot.send_msg(
                    message_type="private",
                    message=MessageSegment.image(
                        await md_to_pic("定时更新失败！\n" + e + "\n\n防风控编码" +
                                        str(time.time()))),
                    user_id=int(adid))


# 每日八点一分向所有群聊播报今日比赛
#TODO 添加群聊/私聊订阅功能，只向订阅了的播报今日比赛
@scheduler.scheduled_job("cron",
                         hour=str(config.broadcast_hour),
                         minute=str(config.broadcast_minute),
                         id="auto_today")
async def auto_today():
    bot = nonebot.get_bot()
    group_list = await bot.get_group_list()
    res = await get_today()
    for group in group_list:
        await bot.send_msg(message_type="group",
                           group_id=group['group_id'],
                           message=res)


# 手动更新
update = on_command('update', priority=1, aliases={'手动更新'})


@update.handle()
async def manual_update(event: MessageEvent):
    try:
        await _update()
        await update.finish("更新成功" + "\n\n防风控编码" + str(time.time()))
    except Exception as e:
        logger.warning("手动更新失败！")
        logger.warning(e)
        await update.finish(
            MessageSegment.image(await
                                 md_to_pic("手动更新失败！\n" + e + "\n\n防风控编码" +
                                           str(time.time()))))


# today今日比赛
today = on_command('today', priority=3, aliases={'今日', '今日比赛', '今天', '今天比赛'})


@today.handle()
async def cmd_today(event: MessageEvent):
    try:
        res = await get_today()
        await today.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await today.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


# 洛谷
preluogu = on_keyword(['preluogu', '洛谷历史'], priority=2, block=True)
luogu = on_keyword(['luogu', '洛谷'], priority=3)


@preluogu.handle()
async def cmd_preluogu(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_preluogu(counts)
        await preluogu.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await preluogu.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


@luogu.handle()
async def cmd_luogu(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_luogu(counts)
        await luogu.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await luogu.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


# CF
precf = on_keyword(['precf'], priority=2, block=True)
cf = on_keyword(['cf'], priority=3)


@precf.handle()
async def cmd_precf(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_precf(counts)
        await precf.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await precf.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


@cf.handle()
async def cmd_cf(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_cf(counts)
        await cf.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await cf.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


# atcoder
preatc = on_keyword(['preatc'], priority=2, block=True)
atc = on_keyword(['atc'], priority=3)


@preatc.handle()
async def cmd_preatc(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_preatc(counts)
        await preatc.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await preatc.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


@atc.handle()
async def cmd_atc(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_atc(counts)
        await atc.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await atc.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


# 牛客
prenc = on_keyword(['prenc', '牛客历史'], priority=2, block=True)
nc = on_keyword(['nc', '牛客'], priority=3)


@prenc.handle()
async def cmd_prenc(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_prenc(counts)
        await prenc.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await prenc.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


@nc.handle()
async def cmd_nc(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_nc(counts)
        await nc.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await nc.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))


# next
_next = on_keyword(['next','近期','近期比赛'], priority=2)


@_next.handle()
async def cmd_next(event: MessageEvent):
    try:
        counts = int(str(event.get_message()).split()[1])
    except:
        counts = 3
    try:
        res = await get_next(counts)
        await _next.finish(MessageSegment.image(await md_to_pic(res)))
    except Exception as e:
        logger.warning("查询失败！")
        logger.warning(e)
        await _next.finish(
            MessageSegment.image(await md_to_pic("查询失败！\n" + e + "\n\n防风控编码" +
                                                 str(time.time()))))
