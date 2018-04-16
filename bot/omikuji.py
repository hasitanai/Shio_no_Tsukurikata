from mastodon import Mastodon
import re, traceback, json, codecs
from datetime import datetime, timedelta, timezone
from bot import conv, toot


def order(x):
    if x == "大吉":
        return 6
    elif x == "中吉":
        return 5
    elif x == "小吉":
        return 4
    elif x == "吉":
        return 3
    elif x == "半吉":
        return 2
    elif x == "末吉":
        return 1
    elif x == "末小吉":
        return 0
    elif x == "凶":
        return -1
    elif x == "小凶":
        return -2
    elif x == "半凶":
        return -3
    elif x == "末凶":
        return -4
    elif x == "大凶":
        return -5


def omikuji(status):
    try:
        account = status['account']
        with open('data\\dic_time\\' + account["acct"] + '.json', 'r') as f:
            if not f == "":
                nstr = json.load(f)
        last_time = datetime.strptime(re.sub(" ..:..:...*", "",
                                             str(conv.delta(str(nstr["omikuji_time"])))), '%Y-%m-%d')
        now_time = datetime.strptime(re.sub(" ..:..:...*", "",
                                             str(conv.delta(str(status['created_at'])))), '%Y-%m-%d')
        if last_time != now_time:
            print("◇Hit_try")
            post = conv.rand_w('bot\\game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
            c = {}
            c.update({"omikuji_time": str(status["created_at"])})
            w = nstr["omikuji_lack"]
            n1 = order(w)
            z = re.search("【(.+)】", post)
            c.update({"omikuji_lack": z.group(1)})
            n2 = order(z.group(1))
            if n2 == 6:
                post = post + "\n大吉です、おめでとうございます。"
            elif n2 == -5:
                post = post + "\n……ご愁傷様です。元気だしてくださいね。"
            elif n1 < n2:
                post = post + "\n前回より運気が上がりましたね。"
            elif n1 > n2:
                post = post + "\n前回より運気が下がりましたね。"
            elif n1 == n2:
                post = post + "\n前回と同じ結果になりましたね。"
            with codecs.open('data\\dic_time\\' + account["acct"] + '.json', 'w+', 'UTF-8') as f:
                json.dump(c, f)
            with codecs.open('data\\dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'r', 'UTF-8') as f:
                a = {}
                a = json.load(f)
            with codecs.open('data\\dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w',
                             'UTF-8') as f:
                a.update({re.sub(" \d{2}:\d{2}:\d{2}\.\d{6}\+00:00", "", str(status['created_at'])): order(
                    z.group(1))})
                json.dump(a, f)
        else:
            s = "\n本日あなたが引いた結果は【{}】です。".format(nstr["omikuji_lack"])
            mastodon = Mastodon(
                client_id="login\\cred.txt",
                access_token="login\\auth.txt",
                api_base_url=open("login\\instance.txt").read())  # インスタンス
            toot.toot_res(mastodon,
                          "@" + account['acct'] + " 一日一回ですよ！\n朝9時頃を越えたらもう一度お願いします！" + s,
                          "public", status["id"], sec=3)
            return
    except FileNotFoundError:
        print("◇hit_New")
        post = conv.rand_w('bot\\game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
        c = {}
        c.update({"omikuji_time": str(status["created_at"])})
        z = re.search("【(.+)】", post)
        c.update({"omikuji_lack": z.group(1)})
        with codecs.open('data\\dic_time\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
            json.dump(c, f)
        with codecs.open('data\\dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
            a = {}
            a.update({re.sub(" \d{2}:\d{2}:\d{2}\.\d{6}\+00:00", "", str(status['created_at'])): order(z.group(1))})
            json.dump(a, f)
    except json.decoder.JSONDecodeError:
        print(traceback.format_exc())
        print("◇hit_ReNew")
        post = conv.rand_w('bot\\game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
        c = {}
        c.update({"omikuji_time": str(status["created_at"])})
        z = re.search("【(.+)】", post)
        c.update({"omikuji_lack": z.group(1)})
        with codecs.open('data\\dic_time\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
            json.dump(c, f)
        with codecs.open('data\\dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
            a = {}
            a.update({re.sub(" \d{2}:\d{2}:\d{2}\.\d{6}\+00:00", "", str(status['created_at'])): order(z.group(1))})
            json.dump(a, f)
    return post
