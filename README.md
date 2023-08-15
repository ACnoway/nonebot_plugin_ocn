# nonebot_plugin_ocn

OI Contest Notifier

订阅洛谷/CF/Atcoder/牛客平台的比赛信息

```
luogu/preluogu(洛谷/洛谷历史) x 查询洛谷近期/历史的x场比赛（x默认为3）
cf/precf x 查询CF近期/历史的x场比赛（x默认为3）
atc/preatc x 查询Atcoder近期/历史的x场比赛（x默认为3）
nc/prenc(牛客/牛客历史) x 查询牛客近期/历史的x场比赛（x默认为3）
today(今日/今日比赛/今天/今天比赛) 查询所有平台今天的比赛
next(近期/近期比赛) x 查询所有平台近期的x场比赛（x默认为3）
update(手动更新) 手动更新缓存
help 输出指令帮助
```

## 注意事项

定时自动更新通知会向所有在.env.dev文件中配置了SUPERUSER的QQ号播报，config.py里有开关，默认开

每日早上八点一分会向列表内所有群聊播报今日比赛，目前无法更改是否向特定群聊播报，可以在config.py里更改时间

## TODO

- [ ] 添加群聊/私聊订阅功能，只向订阅了的播报今日比赛
