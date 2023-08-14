import time
import json
import html
import requests
import datetime
from bs4 import BeautifulSoup

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


async def upd_luogu():
    # 这里调用洛谷api，缓存进文件
    response = requests.get(
        "https://www.luogu.com.cn/contest/list?_contentOnly=any",
        timeout=10,
        headers=headers)
    res = response.text
    pos = res.find("\"code\":200")
    if pos == -1: return
    f = open('./data/luogu.txt', 'w', encoding='utf-8')
    f.write(res)
    f.close()


async def upd_cf():
    # 这里调用cf api，缓存进文件
    response = requests.get(
        "https://codeforces.com/api/contest.list?gym=false",
        timeout=20,
        headers=headers)
    res = response.text
    pos = res.find("unavailable")
    if pos != -1: return
    res = json.dumps(response.json())
    f = open('./data/cf.txt', 'w', encoding='utf-8')
    f.write(res)
    f.close()


async def upd_atc():
    # 这里直接爬取atcoder的比赛界面缓存进文件
    response = requests.get("https://atcoder.jp/contests/",
                            timeout=20,
                            headers=headers)
    res = response.text
    f = open('./data/atc.txt', 'w', encoding='utf-8')
    f.write(res)
    f.close()


async def upd_nowcoder():
    # 这里直接爬取牛客的比赛界面缓存进文件
    response = requests.get("https://ac.nowcoder.com/acm/contest/vip-index",
                            timeout=10,
                            headers=headers)
    res = response.text
    f = open('./data/nc.txt', 'w', encoding='utf-8')
    f.write(res)
    f.close()


async def get_today():
    time_today = datetime.date.today()
    time_today = datetime.datetime.strftime(time_today, '%Y-%m-%d')
    #* 存储oj的名称及网站
    ojs = [["洛谷", "https://www.luogu.com.cn/contest/"],
           ["codeforces", "https://codeforces.com/contest/"],
           ["atcoder", "https://atcoder.jp"],
           ["牛客", "https://ac.nowcoder.com/acm/contest/"]]
    results = []

    #* 洛谷
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回 luogu 的 API
    # response=requests.get("https://codeforces.com/api/contest.list?gym=false")
    # res=json.dumps(response.json())
    f = open('./data/luogu.txt', 'r', encoding='utf-8')
    res = f.read()
    f.close()
    res = json.loads(res)['currentData']['contests']['result']
    for ress in res:
        if ress['endTime'] < time.time():
            break
        name = ress['name']
        DateTime = ress['startTime']
        contest_id = ress['id']
        time_local = time.localtime(DateTime)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        tdtime = time.strftime("%Y-%m-%d", time_local)
        # 加入队列中：网站，名称，时间，id
        if tdtime == time_today:
            results.append([0, name, dt, str(contest_id)])

    #* cf
    # response=requests.get("https://codeforces.com/api/contest.list?gym=false")
    # res=json.dumps(response.json())
    f = open('./data/cf.txt', 'r', encoding='utf-8')
    res = f.read()
    f.close()
    res = json.loads(res)['result']
    for ress in res:
        if ress["phase"] == "FINISHED":
            break
        name = ress['name']
        DateTime = ress['startTimeSeconds']
        contest_id = ress['id']
        time_local = time.localtime(DateTime)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        tdtime = time.strftime("%Y-%m-%d", time_local)
        # 加入队列中：网站，名称，时间，id
        if tdtime == time_today:
            results.append([1, name, dt, str(contest_id)])
    # if cnt_cf!=0 and int(today)!=int(time_now): cnt_cf=0

    #* atcoder
    # response=requests.get("https://atcoder.jp/contests/")
    # res=response.text
    f = open('./data/atc.txt', 'r', encoding='utf-8')
    res = f.read()
    f.close()
    res = BeautifulSoup(res, "html.parser")
    res = res.select('#contest-table-upcoming tbody tr')
    for ress in res:
        name = ress.select('a')[1].text
        DateTime = ress.select('time')[0].text
        last = DateTime.find("+", 0)
        DateTime = DateTime[0:last]
        contest_id = ress.select('a')[1]['href']
        time_local = datetime.datetime.strptime(DateTime, '%Y-%m-%d %H:%M:%S')
        time_local -= datetime.timedelta(hours=1)
        dt = datetime.datetime.strftime(time_local, '%Y-%m-%d %H:%M:%S')
        tdtime = datetime.datetime.strftime(time_local, '%Y-%m-%d')
        # 加入队列中：网站，名称，时间，id
        if tdtime == time_today:
            results.append([2, name, dt, contest_id])
    # if cnt_atc!=0 and int(today)!=int(time_now): cnt_atc=0

    #* 牛客
    # response=requests.get("https://ac.nowcoder.com/acm/contest/vip-index")
    # res=response.text
    f = open('./data/nc.txt', 'r', encoding='utf-8')
    res = f.read()
    f.close()
    res = BeautifulSoup(res, "html.parser")
    res = res.select('.platform-mod.js-current .platform-item.js-item')
    for ress in res:
        # 选择比赛介绍
        cont = json.loads(html.unescape(ress.get('data-json')))
        name = cont['contestName']
        DateTime = cont['contestStartTime']
        contest_id = cont['contestId']
        time_local = time.localtime(DateTime // 1000)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        tdtime = time.strftime("%Y-%m-%d", time_local)
        # 加入队列中：网站，名称，时间，id
        if tdtime == time_today:
            results.append([3, name, dt, str(contest_id)])
    # if cnt_nowcoder!=0 and int(today)!=int(time_now): cnt_nowcoder=0
    results = sorted(results, key=lambda x: (x[2], x[0]))
    #* 统计答案
    ans = ""
    if len(results) == 0:
        return '今天没有比赛哦 =￣ω￣=' + "\n\n防风控编码" + str(time.time())
    else:
        for conts in results:
            ans += "\n\n比赛平台：" + ojs[conts[0]][0]
            ans += "\n比赛名称：" + conts[1]
            ans += "\n比赛时间：" + conts[2]
            ans += "\n比赛链接：" + ojs[conts[0]][1] + conts[3]
        return '找到今天的比赛如下：' + ans + "\n\n防风控编码" + str(time.time())


async def get_preluogu(counts):
    results = []

    f = open('luogu.txt', 'r', encoding='utf-8')
    res = f.read()
    f.close()
    res = json.loads(res)['currentData']['contests']['result']
    for ress in res:
        if ress['endTime'] > time.time():
            continue
        name = ress['name']
        DateTime = ress['startTime']
        contest_id = ress['id']
        time_local = time.localtime(DateTime)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        # 加入队列中：名称，时间，id
        results.append([name, dt, str(contest_id)])
        if len(results) >= counts:
            break
    if len(results) == 0:
        return "居然找不到，可能是：\n1. bot裂了\n2. 网站裂了\n3. 缓存裂了\n4. 地球裂了" + "\n\n防风控编码" + str(
            time.time())
    else:
        kaitou = '<div align="center">\n <h1> 洛谷历史比赛 </h1> \n</div>\n'
        ans = "<ol>\n"
        for conts in results:
            ans += "<li>\n<ul>"
            ans += f"\n<li>比赛名称：{conts[0]}</li>"
            ans += f"\n<li>比赛时间：{conts[1]}</li>"
            ans += f"\n<li>比赛链接：https://www.luogu.com.cn/contest/{conts[2]}</li>"
            ans += "</ul>\n</li>\n"
        ans+="</ol>"
        if len(results) < counts:
            return kaitou + f'缓存中洛谷历史比赛不足 {str(counts)} 场，找到历史 {str(len(results))} 场比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'
        else:
            return kaitou + f'找到历史 {str(len(results))} 场洛谷比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'


async def get_luogu(counts):
    results = []

    f = open('luogu.txt', 'r', encoding='utf-8')
    res = f.read()
    f.close()
    res = json.loads(res)['currentData']['contests']['result']
    for ress in res:
        if ress['endTime'] < time.time():
            break
        name = ress['name']
        DateTime = ress['startTime']
        contest_id = ress['id']
        time_local = time.localtime(DateTime)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        # 加入队列中：名称，时间，id
        results.insert(0, [name, dt, str(contest_id)])
        if len(results) >= counts:
            break
    if len(results) == 0:
        return "没有找到近期的洛谷比赛哦" + "\n\n防风控编码" + str(time.time())
    else:
        kaitou = '<div align="center">\n <h1> 洛谷近期比赛 </h1> \n</div>\n'
        ans = "<ol>\n"
        for conts in results:
            ans += "<li>\n<ul>"
            ans += f"\n<li>比赛名称：{conts[0]}</li>"
            ans += f"\n<li>比赛时间：{conts[1]}</li>"
            ans += f"\n<li>比赛链接：https://www.luogu.com.cn/contest/{conts[2]}</li>"
            ans += "</ul>\n</li>\n"
        ans+="</ol>"
        if len(results) < counts:
            return kaitou + f'洛谷近期比赛不足 {str(counts)} 场，找到近期 {str(len(results))} 场比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'
        else:
            return kaitou + f'找到近期 {str(len(results))} 场洛谷比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'


async def get_precf(counts):
    results = []
    
    f = open('cf.txt', 'r',encoding='utf-8')
    res = f.read()
    f.close()
    res = json.loads(res)['result']
    for ress in res:
        if ress["phase"] != "FINISHED":
            continue
        name=ress['name']
        DateTime=ress['startTimeSeconds']
        contest_id=ress['id']
        time_local=time.localtime(DateTime)
        dt=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        # 加入队列中：名称，时间，id
        results.append([name,dt,str(contest_id)])
        if len(results) >= counts:
            break
    if len(results)==0:
        return "居然找不到，可能是：\n1. bot裂了\n2. 网站裂了\n3. 缓存裂了\n4. 地球裂了"+"\n\n防风控编码"+str(time.time())
    else:
        kaitou = '<div align="center">\n <h1> Codeforces历史比赛 </h1> \n</div>\n'
        ans = "<ol>\n"
        for conts in results:
            ans += "<li>\n<ul>"
            ans += f"\n<li>比赛名称：{conts[0]}</li>"
            ans += f"\n<li>比赛时间：{conts[1]}</li>"
            ans += f"\n<li>比赛链接：https://codeforces.com/contest/{conts[2]}</li>"
            ans += "</ul>\n</li>\n"
        ans+="</ol>"
        if len(results) < counts:
            return kaitou + f'缓存中CF历史比赛不足 {str(counts)} 场，找到历史 {str(len(results))} 场比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'
        else:
            return kaitou + f'找到历史 {str(len(results))} 场CF比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'


async def get_cf(counts):
    results = []
    
    # response=requests.get("https://codeforces.com/api/contest.list?gym=false")
    f = open('cf.txt', 'r',encoding='utf-8')
    res = f.read()
    f.close()
    res = json.loads(res)['result']
    for ress in res:
        if ress["phase"] == "FINISHED":
            break
        name=ress['name']
        DateTime=ress['startTimeSeconds']
        contest_id=ress['id']
        time_local=time.localtime(DateTime)
        dt=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        # 加入队列中：名称，时间，id
        results.insert(0,[name,dt,str(contest_id)])
        if len(results) >= counts:
            break
    results = sorted(results, key=lambda x: (x[1]))
    if len(results)==0:
        return "没有找到要开始的codeforces比赛哦"+"\n\n防风控编码"+str(time.time())
    else:
        kaitou = '<div align="center">\n <h1> Codeforces近期比赛 </h1> \n</div>\n'
        ans = "<ol>\n"
        for conts in results:
            ans += "<li>\n<ul>"
            ans += f"\n<li>比赛名称：{conts[0]}</li>"
            ans += f"\n<li>比赛时间：{conts[1]}</li>"
            ans += f"\n<li>比赛链接：https://codeforces.com/contest/{conts[2]}</li>"
            ans += "</ul>\n</li>\n"
        ans+="</ol>"
        if len(results) < counts:
            return kaitou + f'CF近期比赛不足 {str(counts)} 场，找到近期 {str(len(results))} 场比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'
        else:
            return kaitou + f'找到近期 {str(len(results))} 场CF比赛如下：\n' + ans + f'\n\n防风控编码 {str(time.time())}\n'

if __name__ == '__main__':
    print(1)