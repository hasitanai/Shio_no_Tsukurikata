# -*- coding: utf-8 -*-

from mastodon import *
from time import time, sleep
import feedparser
import re, sys, os, csv, json, codecs, io, gc
import threading, requests, random
from datetime import datetime, date
from pytz import timezone
import warnings, traceback
from xml.sax.saxutils import unescape as unesc
import numpy as np

"""
上記必要なものはpipしていってね！！！
reは正規表現検索用　sysとjsonは多分何かの基盤
threadingはマルチ稼働のため　csvはトゥート保管のデータ形式のため。
codecsは文字化け処理用。　randomは文字通りランダムにするためのもの。
osフォルダ参照用。tracebackはエラー報告のデバック用。
datetime, timezoneは時間記録用。
warningsは……分からん！！！！
今後入れる予定のモジュ「Numpy」
"""

# プロンプトで起動したい人のための装置
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)

# これはよく分かってない
warnings.simplefilter("ignore", UnicodeWarning)

"""
ログイントークン取得済みで動かしてね（*'∀'人）
自分はこちらの記事を参照しましたのでアクセストークン各自で取ってね(*'ω'*)
https://routecompass.net/mastodon/
"""
url_ins = open("instance.txt").read()  # instanceのアドレスお願いね　例：https://knzk.me

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

print("こおり「ログイン、完了しました。」")


def back01():
    print("---timeline遡りチェックテスト---")
    tl = mastodon.timeline_local()
    for status in tl:
        print("---API_LOCAL【遡り】---")
        Log(status).read()
        res.fav01(status)
        sleep(1)


class Re1():  # Content整頓用関数
    def text(text):
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|</span>|</a>|<span class="[a-z-]+">', "",
                       str(text)))


class Log():  # toot記録用クラス٩(๑❛ᴗ❛๑)۶
    def __init__(self, status):
        self.account = status["account"]
        self.mentions = status["mentions"]
        self.content = unesc(Re1.text(status["content"]))
        self.non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

    def read(self):
        name = self.account["display_name"]
        acct = self.account["acct"]
        non_bmp_map = self.non_bmp_map
        print(str(name).translate(non_bmp_map) + "@" + str(
            acct).translate(self.non_bmp_map))
        print(str(self.content).translate(non_bmp_map))
        print(str(self.mentions).translate(non_bmp_map))

    def write(self):
        text = self.content
        acct = self.account["acct"]
        f = codecs.open('log\\' + 'log_' + nowing + '.txt', 'a', 'UTF-8')
        f.write(re.sub('<br />', '\\n', str(text)) + ',<acct="' + acct + '">\r\n')
        f.close()


class User(StreamListener):  # ホームでフォローした人と通知を監視するStreamingAPIの継承クラスです。
    def on_notification(self, notification):  # 通知を監視します。
        try:
            print(("===●user_on_notification【{}】●===").format(str(notification["type"])))
            account = notification["account"]
            if notification["type"] == "follow":  # 通知がフォローだった場合はフォロバします。
                print(account["display_name"])
                sleep(2)
                mastodon.account_follow(account["id"])
                print("◇フォローを返しました。")

            elif notification["type"] == "mention":  # 通知がリプだった場合です。
                status = notification["status"]
                log = threading.Thread(Log(status).read())
                log.run()
                if account["acct"] != "1":
                    men.mention(status)

            elif notification["type"] == "favourite":  # 通知がベルのときです。
                status = notification["status"]
                print("{0} @{1} さんがベルを鳴らしました。".format(account["display_name"], account["acct"]))
                if account["acct"] == "Knzk":
                    count.knzk_fav += 1
                    print("神崎にふぁぼられた数:" + str(count.knzk_fav))
                    if count.knzk_fav == 10:
                        f = codecs.open('res\\fav_knzk.txt', 'r', 'utf-8')
                        l = []
                        for x in f:
                            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
                        f.close()
                        m = len(l)
                        s = random.randint(1, m)
                        post = (l[s - 1])
                        g_vis = "public"
                        bot.toot_res(post, g_vis)
                        count.knzk_fav = 0

            elif notification["type"] == "reblog":  # 通知がブーストのときです。
                print("{0} @{1} さんがブーストしました。".format(account["display_name"], account["acct"]))
        except IncompleteRead:
            print("【USER】接続が切れました。")
            pass
        except Exception as e:
            e_me()
            pass
        print("   ")
        pass


class Local(StreamListener):  # ここではLTLを監視する継承クラスになります。
    def on_update(self, status):  # StreamingAPIがリアルタイムにトゥート情報を吐き出してくれます。
        try:
            print("===○local_on_update○===")
            if count.dev_mode is True:
                non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                print(str(status).translate(non_bmp_map))
            else:
                log = threading.Thread(Log(status).read())
                log.run()
            if count.log_save is True:
                Log(status).write()
            ltl = threading.Thread(TL.local(status))
            ltl.run()
            pass

        except IncompleteRead:
            e_me()
            pass
        print("   ")
        pass

    def on_delete(self, status_id):  # トゥー消し警察の監視場になります。
        try:
            print(str("===×on_delete【{}】×===").format(str(status_id)))
            pass
        except Exception as e:
            """
            print("エラー情報【DELETE】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.white("【" + jst_now + "】\n")
                traceback.print_exc(file=f)
                f.white("\n")
            e_me()
            """
            pass


"""
「mastodon.」メソッドを下記の関数によって「ホーム」「連合」「ローカル」「指定のハッシュタグ」が選択できます
 user_stream, public_stream, local_stream, hashtag_stream(self, tag, listener, async=False)
StreamingAPIでトゥートを参照することによりAPIの節約ができます。是非活用していきましょう（*'∀'人）
"""


class men():  # メンションに対する処理です。
    def mention(status):
        account = status["account"]
        mentions = Re1.text(status["mentions"])
        content = Re1.text(status["content"])
        media_files = None
        if account['acct'] != "1":
            if re.compile("こおり(.*)(ネイティオ|ねいてぃお)(.*)鳴").search(content):
                post = "@" + str(account["acct"]) + " " + "ネイティオさん、私が起きてから" + str(
                    count.twotwo) + "回鳴きました。"
                g_vis = status["visibility"]
                sec = 5
            elif re.compile("トゥートゥートゥー？|ﾄｩｰﾄｩｰﾄｩｰ?").search(content):
                post = "@" + str(account["acct"]) + " " + "トゥートゥー、トゥートゥトゥトゥ「" + str(count.twotwo) + "」"
                g_vis = status["visibility"]
                sec = 5
            elif re.compile("\d+[dD]\d+").search(content):
                coro = (re.sub("@1", "", str(content)))
                post = "@" + str(account["acct"]) + "\n" + game.dice(coro)
                g_vis = status["visibility"]
                sec = 5
            elif re.compile("(アラーム|[Aa][Rr][Aa][Mm])(\d+)").search(content):
                post, sec = game.aram(status)
                g_vis = status["visibility"]
            elif re.compile('みくじ(.*)(おねが(.*)い|お願(.*)い|[引ひ]([きく]|いて)|や[りる]|ください|ちょうだい|(宜|よろ)しく|ひとつ|し(て|たい))').search(content):
                if account['acct'] != "1":
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
                    try:
                        with codecs.open('dic_time\\' + account["acct"] + '.json', 'r', 'UTF-8') as f:
                            nstr = json.load(f)
                        last_time = datetime.strptime(re.sub("T..:..:..\....Z", "", nstr["omikuji_time"]), '%Y-%m-%d')
                        now_time = datetime.strptime(re.sub("T..:..:..\....Z", "", status['created_at']), '%Y-%m-%d')
                        if last_time != now_time:
                            print("◇Hit_try")
                            post = bot.rand_w('game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
                            c = {}
                            c.update({"omikuji_time":str(status["created_at"])})
                            w = nstr["omikuji_lack"]
                            n1 = order(w)
                            z = re.search("【(.+)】", post)
                            c.update({"omikuji_lack":z.group(1)})
                            n2 = order(z.group(1))
                            if n2 == 6:
                                post = post + "\n大吉です、おめでとうございます。"
                            elif n2 == -5:
                                post = post + "\n……ご愁傷様です。元気だしてくださいね。"
                            elif n1 < n2:
                                post = post + "\n前回より運気が上がりましたね。"
                            elif  n1 > n2:
                                post = post + "\n前回より運気が下がりましたね。"
                            elif n1 == n2:
                                post = post + "\n前回と同じ結果になりましたね。"
                            with codecs.open('dic_time\\' + account["acct"] + '.json', 'w+', 'UTF-8') as f:
                                json.dump(c, f)
                            with codecs.open('dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'r', 'UTF-8') as f:
                                a = {}
                                a = json.load(f)
                            with codecs.open('dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                                a.update({re.sub("T..:..:..\....Z", "", status['created_at']): order(z.group(1))})
                                json.dump(a, f)
                        else:
                            s = "\n本日あなたが引いた結果は【{}】です。".format(nstr["omikuji_lack"])
                            bot.toot_res("@" + account['acct'] + " 一日一回ですよ！\n朝9時頃を越えたらもう一度お願いします！" + s,
                                         "public", status["id"], sec=3)
                    except FileNotFoundError:
                        print("◇hit_New")
                        post = bot.rand_w('game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
                        c = {}
                        c.update({"omikuji_time":str(status["created_at"])})
                        z = re.search("【(.+)】", post)
                        c.update({"omikuji_lack":z.group(1)})
                        with codecs.open('dic_time\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                            json.dump(c, f)
                        with codecs.open('dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                            a = {}
                            a.update({re.sub("T..:..:..\....Z", "", status['created_at']): order(z.group(1))})
                            json.dump(a, f)
                    g_vis = status["visibility"]
                    sec = 5
            elif re.compile('たこ[焼や]き(.*)([焼や]いて|作って|つくって|['
                            '食た]べたい|おねがい|お願い|ちょ[うー]だい|[欲ほ]しい)').search(content):
                print("◇Hit")
                sleep(5)
                l = []
                f = codecs.open('res\\takoyaki.txt', 'r', 'utf-8')
                for x in f:
                    l.append(x.rstrip("\r\n|\ufeff").replace('\\n', '\n'))
                f.close()
                m = len(l)
                s = random.randint(1, m)
                post = "@" + str(account["acct"]) + "\n" + l[s - 1]
                f = codecs.open('res_med\\takoyaki.txt', 'r', 'utf-8')
                j = []
                for x in f:
                    j.append(x.rstrip("\r\n").replace('\\n', '\n'))
                f.close()
                xxx = re.sub("(.*)\.", "", j[s - 1])
                media_files = [mastodon.media_post("media\\" + j[s - 1], "image/" + xxx)]
                print("◇メディア選択しました")
                print(j[s - 1])
                g_vis = "public"
                sec = 5
            elif re.compile('デバック|[dD][eE][vV]|でばっく').search(content) and account['acct'] == "0":
                if re.compile('ON|on|おん|オン').search(content):
                    count.dev_mode = True
                    post = "@" + str(account["acct"]) + " " + "デバックモード始めます。"
                elif re.compile('OFF|off|おふ|オフ').search(content):
                    count.dev_mode = False
                    post = "@" + str(account["acct"]) + " " + "デバックモード終わります。"
                g_vis = status["visibility"]
                sec = 2
            else:
                global api_Bot
                url = "https://chatbot-api.userlocal.jp/api/chat"  # 人工知能APIサービス登録してお借りしてます。
                s = requests.session()
                mes = (re.sub("<p>|</p>", "", str(content)))
                params = {
                    'key': api_Bot,  # 登録するとAPIKeyがもらえますのでここに入れます。
                    'message': mes,
                }
                r = s.post(url, params=params)
                ans = json.loads(r.text)
                post = "@" + str(account["acct"]) + " " + ans["result"]
                g_vis = status["visibility"]
                sec = 5
            if post is not None:
                in_reply_to_id = status["id"]
                t = threading.Timer(sec, bot.toot, [post, g_vis, in_reply_to_id, media_files, None])
                t.start()
            else:
                pass


class TL():  # ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
    def local(status):
        account = status["account"]
        check.check01(status)
        if account["acct"] != "1":
            res.fav01(status)
            res.res01(status)
            res.res02(status)
            res.res03(status)
            res.res04(status)
            res.res05(status)
            res.y(status)
            game.omikuji(status)
            game.land(status)
            res.EFB(status)
        check.check02(status)
        check.check03(status)
        check.check00(status)
        check.twotwo(status)
        check.media(status)
        gc.collect()

    def home(status):
        gc.collect()
        pass


class bot():
    def __init__(self):
        self.status = status
        self.content = Re1.text(status["content"])
        self.account = status["account"]
        self.g_vis = "public"
        self.in_reply_to_id = None
        self.media_files = None

    def toot(post, g_vis="public", in_reply_to_id=None, media_files=None, spoiler_text=None):  # トゥートする関数処理だよ！
        print(in_reply_to_id)
        mastodon.status_post(status=post, visibility=g_vis, in_reply_to_id=in_reply_to_id, media_ids=media_files,
                             spoiler_text=spoiler_text)

    def toot_res(post, g_vis="public", in_reply_to_id=None,
                 media_files=None, spoiler_text=None, sec=2):  # Postする内容が決まったらtoot関数に渡します。
        # その後は直ぐに連投しないようにクールタイムを挟む処理をしてます。
        if count.learn_toot != post:
            count.learn_toot = post
            now = time()
            delay = now - count.CT
            loss = count.end - int(delay)
            if loss < 0:
                loss = 0
            ing = sec + loss
            t = threading.Timer(ing, bot.toot, [post, g_vis, in_reply_to_id, media_files, spoiler_text])
            t.start()
            print("【次までのロスタイム:" + str(count.end + sec) + "】")
            s = threading.Timer(ing, bot.res, [sec])
            s.start()
            del t
            del s
            gc.collect()
            count.CT = time()
            count.end = ing
            z = threading.Timer(60, bot.t_forget)  # クールタイム伸ばした。
            z.start()

    def BellBaku(fav):
        s = time()
        while 1:
            e = time()
            t = e - s
            if t >= 5:
                mastodon.status_favourite(fav)
                break
            else:
                mastodon.status_favourite(fav)
                mastodon.status_unfavourite(fav)

    def fav_now(status):  # ニコります
        fav = status["id"]
        mastodon.status_favourite(fav)
        print("◇Fav")

    def reb_now(status):  # ブーストします
        reb = status["id"]
        mastodon.status_reblog(reb)
        print("◇Reb")

    def rand_w(txt_deta):
        f = codecs.open(txt_deta, 'r', 'utf-8')
        l = []
        for x in f:
            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
        f.close()
        m = len(l)
        s = random.randint(1, m)
        return l[s - 1]

    def res(sec):
        count.end = count.end - sec
        if count.end < 0:
            count.end = 0

    def t_forget():  # 同じ内容を連投しないためのクールタイムです。
        count.learn_toot = ""
        print("◇前のトゥート内容を忘れました")


class res():
    def res01(status):  # お返事関数シンプル版。
        content = Re1.text(status["content"])
        with codecs.open('reply.csv', 'r', "UTF-8", "ignore") as f:
            for row in csv.reader(f):
                if re.compile(row[2]).search(content):
                    print("◇Hit")
                    post = row[1].replace('\\n', '\n')
                    bot.toot_res(post, "public", )

    def res02(status):  # 該当するセリフからランダムtootが選ばれてトゥートします。
        content = Re1.text(status["content"])
        with codecs.open('reply_random.csv', 'r', "UTF-8", "ignore") as f:
            for row in csv.reader(f):
                if re.compile(row[2]).search(re.sub("<p>|</p>", "", content)):
                    print("◇Hit")
                    post = bot.rand_w('res\\' + row[1] + '.txt')
                    bot.toot_res(post, "public", sec=int(row[0]))
                    return

    def res03(status):  # 該当する文字があるとメディアをアップロードしてトゥートしてくれます。
        content = Re1.text(status["content"])
        with codecs.open('reply_media.csv', 'r', "UTF-8", "ignore") as f:
            for row in csv.reader(f):
                if re.compile(row[2]).search(re.sub("<p>|</p>", "", content)):
                    print("◇Hit")
                    l = []
                    with codecs.open('res\\' + row[1] + '.txt', 'r', 'utf-8') as f:
                        for x in f:
                            l.append(x.rstrip("\r\n|\ufeff").replace('\\n', '\n'))
                    m = len(l)
                    s = random.randint(1, m)
                    post = l[s - 1]
                    with codecs.open('res_med\\' + row[3] + '.txt', 'r', 'utf-8') as f:
                        j = []
                        for x in f:
                            j.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    xxx = re.sub("(.*)\.", "", j[s - 1])
                    media_files = [mastodon.media_post("media\\" + j[s - 1])]
                    print("◇メディア選択しました")
                    print(j[s - 1])
                    bot.toot_res(post, "public", None, media_files, None, int(row[0]))
                    return

    def res04(status):  # こおりちゃん式挨拶機能の実装
        account = status["account"]
        content = re.sub("<p>|</p>", "", str(status['content']))
        try:
            if account["acct"] != "1":  # 一人遊びで挨拶しないようにするための処置
                try:
                    with codecs.open('oyasumi\\' + account["acct"] + '.txt', 'r', 'UTF-8') as f:
                        zzz = f.read()
                except:
                    print("◇初めての人に会いました。")
                    if account['display_name'] == "":
                        post = account['acct']+ "さん\n" + "はじめまして、よろしくお願いいたします。"
                    else:
                        post = account['display_name'] + "さん\n" + "はじめまして、よろしくお願いいたします。"
                    g_vis = "public"
                    bot.toot_res(post, "public", sec=5)
                    f = codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8')
                    f.write("active")
                    f.close()
                    zzz = ""
                if zzz == "good_night":
                    try:
                        with codecs.open('dic_time\\' + account["acct"] + '.json', 'r', 'UTF-8') as f:
                            nstr = json.load()
                        tstr = re.sub("\....Z", "", nstr["sleep"])
                        last_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                        nstr = status['created_at']
                        tstr = re.sub("\....Z", "", nstr)
                        now_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                        delta = now_time - last_time
                        if delta.total_seconds() < 600:
                            pass
                        elif delta.total_seconds() >= 600:
                            print("◇Hit")
                            post = account['display_name'] + "さん\n" + bot.rand_w('time\\mada.txt')
                            g_vis = "public"
                            bot.toot_res(post, "public", sec=5)
                            with codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                                f.write("active")
                            return
                        elif delta.total_seconds() >= 3600:
                            print("◇Hit")
                            post = account['display_name'] + "さん\n" + bot.rand_w('time\\oha.txt')
                            g_vis = "public"
                            bot.toot_res(post, "public", sec=5)
                            with codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                                f.write("active")
                            return
                    except:
                        print("◇Hit_エラー回避")
                        post = account['display_name'] + "さん\n" + bot.rand_w('time\\oha.txt')
                        g_vis = "public"
                        bot.toot_res(post, "public", sec=5)
                        with codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                            f.write("active")
                elif zzz == "active":
                    with codecs.open('at_time\\' + account["acct"] + '.txt', 'r', 'UTF-8') as f:
                        nstr = f.read()
                    tstr = re.sub("\....Z", "", nstr)
                    last_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                    nstr = status['created_at']
                    tstr = re.sub("\....Z", "", nstr)
                    now_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                    delta = now_time - last_time
                    if delta.total_seconds() >= 604800:
                        to_r = bot.rand_w('time\\ohisa.txt')
                        print("◇Hit")
                        if account['display_name'] == "":
                            post = account['acct']+ "さん\n" + to_r
                        else:
                            post = account['display_name'] + "さん\n" + to_r
                        return bot.toot_res(post, "public", sec=5)
                    elif delta.total_seconds() >= 75600:
                        if now_time.hour in range(3, 9):
                            to_r = bot.rand_w('time\\kon.txt')
                        elif now_time.hour in range(9, 20):
                            to_r = bot.rand_w('time\\kob.txt')
                        else:
                            to_r = bot.rand_w('time\\oha.txt')
                        print("◇Hit")
                        if account['display_name'] == "":
                            post = account['acct']+ "さん\n" + to_r
                        else:
                            post = account['display_name'] + "さん\n" + to_r
                        return bot.toot_res(post, "public", sec=5)
                    elif delta.total_seconds() >= 28800:
                        to_r = bot.rand_w('time\\hallo.txt')
                        print("◇Hit")
                        if account['display_name'] == "":
                            post = account['acct']+ "さん\n" + to_r
                        else:
                            post = account['display_name'] + "さん\n" + to_r
                        return bot.toot_res(post, "public", sec=5)
        except:
            print("◇失敗しました。")
            f = codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8')
            f.write("active")
            f.close()
            e_me()



    def res05(status):
        content = Re1.text(status["content"])
        if re.compile("こおり(.*)[1-5][dD]\d+").search(content):
            print("○hitしました♪")
            account = status["account"]
            post = "@" + str(account["acct"]) + "\n" + game.dice(content)
            bot.toot_res(post, status["visibility"], None, None, "サイコロ振りますね。", 3)

    def y(status):
        content = Re1.text(status["content"])
        account = status["account"]
        if count.y == True:
            if re.compile("こおり.*ねじりサーチ.*[OoＯｏ][FfＦｆ][FfＦｆ]").search(status['content']):
                if account["acct"] == "y" or account["acct"] == "0":
                    count.y = False
                    return bot.toot_res("ねじりサーチ、終了しました。", sec=3)
            elif re.compile("ねじりわさび|ねじり|わさび|ねじわさ|[Kk]nzk[Aa]pp|神崎丼アプリ").search(status['content']):  # 抜き出し
                if account["acct"] is not "y" or account["acct"] is not "1":  # 自分とねじりわさびさんを感知しないように
                    yuzu = re.search("(ねじりわさび|ねじり|わさび|ねじわさ|[Kk]nzk[Aa]pp|神崎丼アプリ)", content)
                    post = ("@y {}を感知しました。").format(str(yuzu.group(1)))
                    return bot.toot(post, "direct", status["id"], None, None)

        else:
            if account["acct"] == "y" or account["acct"] == "0":
                if re.compile("こおり.*ねじりサーチ.*[OoＯｏ][NnＮｎ]").search(status['content']):
                    count.y = True
                    return bot.toot_res("ねじりサーチ、スタートです！", sec=3)

    def fav01(status):  # 自分の名前があったらニコブーして、神崎があったらニコります。
        account = status["account"]
        if account["acct"] != "1":  # 自分以外
            if re.compile("こおり|(神[埼崎]|knzk|(100|5000兆)db)").search(status['content']):
                v = threading.Timer(1, bot.fav_now, [status])
                v.start()
            else:
                pass
            if re.compile("こおり").search(status['content']):
                b = threading.Timer(2, bot.reb_now, [status])
                b.start()
            else:
                pass

    def EFB(status):
        content = Re1.text(status["content"])
        account = status["account"]
        if account["acct"] != "1":
            if re.compile("エターナルフォースブリザード|えたーなるふぉーすぶりざーど").search(content):
                fav = status["id"]
                post = "@" + account["acct"] + " エターナルフォースブリザード……！！"
                in_reply_to_id = status["id"]
                t1 = threading.Timer(3, bot.toot, [post, "public", in_reply_to_id, None, None])
                t1.start()
                t2 = threading.Timer(3, bot.BellBaku, [fav])
                t2.start()


class check():
    def check00(status):
        account = status["account"]
        ct = account["statuses_count"]
        if account["acct"] == "1":
            ct += 1
            if re.match('^\d+000$', str(ct)):
                post = str(ct) + 'toot、達成しました……！\n#こおりキリ番記念'
                g_vis = "public"
                bot.toot_res(post, "public", sec=5)
        else:
            if re.match('^\d+0000$', str(ct)):
                post = "@" + account['acct'] + "\n" + str(
                    ct) + 'toot、おめでとうございます！'
                g_vis = "public"
                bot.toot_res(post, "public", sec=5)
            elif re.match('^\d000$', str(ct)):
                post = "@" + account['acct'] + "\n" + str(
                    ct) + 'toot、おめでとうございます。'
                g_vis = "public"
                bot.toot_res(post, "public", sec=5)

    def check01(status):  # アカウント情報の更新
        account = status["account"]
        created_at = status['created_at']
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        with codecs.open('acct\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
            f.write(str(status["account"]).translate(non_bmp_map))

    def check02(status):  # 最後にトゥートした時間の記憶
        account = status["account"]
        created_at = status['created_at']
        with codecs.open('at_time\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
            f.write(str(status["created_at"]))  # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z

    def check03(status):  # お休みする人を記憶
        account = status["account"]
        content = re.sub("<p>|</p>", "", str(status['content']))
        if account["acct"] != "1":  # 一人遊びで挨拶しないようにっするための処置
            if re.compile("[寝ね](ます|る|マス)([よかぞね]?|[…。うぅー～！]+)$|"
                          "[寝ね](ます|る|マス)(.*)[ぽお]や[すし]").search(content):
                print("◇Hit")
                if account['display_name'] == "":
                    post = account['acct']+ "さん\n" + bot.rand_w('time\\oya.txt')
                else:
                    post = account['display_name'] + "さん\n" + bot.rand_w('time\\oya.txt')
                bot.toot_res(post, "public", sec=5)
                with codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:
                    f.write("good_night")
                with codecs.open('dic_time\\' + account["acct"] + '.json', 'r', 'UTF-8') as f:
                    zzz = {}
                    zzz = json.load(f)
                with codecs.open('dic_time\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                    zzz.update({"sleep":str(status["created_at"])})
                    json.dump(zzz, f)
                print("◇寝る人を記憶しました")
            """
            elif re.compile("こおり(.*)[ぽお]や[すし]").search(status['content']):
                print("◇Hit")
                if account['display_name'] == "":
                    post = account['acct']+ "さん\n" + bot.rand_w('time\\oya.txt')
                else:
                    post = account['display_name'] + "さん\n" + bot.rand_w('time\\oya.txt')
                bot.toot_res(post, "public", sec=5)
            """

    def fav01(status):  # 自分の名前があったらニコブーして、神崎があったらニコります。
        account = status["account"]
        if account["acct"] != "1":  # 自分以外
            if re.compile("こおり|(神[埼崎]|knzk|(100|5000兆)db)").search(status['content']):
                v = threading.Timer(1, bot.fav_now, [status])
                v.start()
            else:
                pass
            if re.compile("こおり").search(status['content']):
                b = threading.Timer(2, bot.reb_now, [status])
                b.start()
            else:
                pass

    def twotwo(status):  # ネイティオが鳴いた数を監視しまーすｗｗｗｗｗ
        account = status["account"]
        if account["acct"] == "twotwo":
            if re.compile("トゥ|ﾄｩ").search(re.sub("<p>|</p>", "", status['content'])):
                count.twotwo += 1
                print("ネイティオが鳴いた数:" + str(count.twotwo))

    def media(status):  # 画像監視機能つけてみました
        account = status["account"]
        if account["acct"] != "1":  # 自分以外
            if status['media_attachments'] == []:
                pass
            else:
                b = threading.Timer(2, bot.reb_now, [status])
                b.start()
                # 通知レイプは合意じゃないので
                """
                med = status['media_attachments']
                post = ("@0 \nid :"+status["id"]+"\nacct: "+account["acct"]+
                        "\n"+status['url'])
                bot.toot_res(post, "direct", status["id"], None, "メディアを検知しました")
                """
                pass


class count():
    knzk_fav = 0
    CT = 0
    end = 0
    learn_toot = ""
    twotwo = 0
    f = codecs.open('game\\bals.txt', 'r', 'utf-8')
    bals = f.read()
    bals = int(bals)
    f.close
    y = False
    dev_mode = False
    log_save = False


class RSS():
    def rss(RSS_URL="https://github.com/GenkaiDev/mastodon/commits/knzk-master.atom"):
        rss_dic = feedparser.parse(RSS_URL)
        # print(rss_dic.feed.title)
        for entry in rss_dic.entries:
            title = entry.title
            link = entry.link
            # print(link)
            # print(title)
        RSS.title = rss_dic.entries[0].title
        RSS.link = rss_dic.entries[0].link

    def main():
        RSS.rss()
        toot_now = RSS.title + "\n" + RSS.link
        #    mastodon.status_post(status=toot_now, media_ids=media_files, visibility=unlisted)
        mastodon.status_post(status=toot_now, visibility="public", spoiler_text="テストします")


class game():
    def dice(inp):
        l = []
        n = []
        m = []
        x = 0
        try:
            inp = re.sub("&lt;", "<", str(inp))
            inp = re.sub("&gt;", ">", str(inp))
            com = re.search("(\d+)[dD](\d+)([:<>]*)(\d*)([\+\-\*/\d]*)(.*)", str(inp))
            print(str(com.group()))
            for v in range(1, 7):
                m.append(com.group(v))
            print(m)
            if int(m[1]) == 0:
                result = "面がないので振りません"
            elif int(m[0]) >= 51:
                result = "回数が多いので振りません"
            elif int(m[0]) == 0:
                result = "回数0なので振りません"
            else:
                print("○サイコロ振ります")
                for var in range(0, int(m[0])):
                    num = random.randint(1, int(m[1]))
                    num = str(num)
                    print(num)
                    if m[4] == True:
                        ad = m[4]
                    else:
                        ad = ""
                    try:
                        if ad == "":
                            dd = 0
                        else:
                            dd = int(ad)
                        if m[5] == "":
                            fd = "［" + m[3] + m[4] + "］→"
                        else:
                            fd = "［" + m[5] + "(" + m[3] + m[4] + ")］→"
                        sd = ad + fd
                        if str(m[2]) == ">":
                            if int(num) >= int(m[3]) + dd:
                                result = "ｺﾛｺﾛ……" + num + sd + "成功"
                            else:
                                result = "ｺﾛｺﾛ……" + num + sd + "失敗"
                        else:
                            if int(num) + dd <= int(m[3]) + dd:
                                result = "ｺﾛｺﾛ……" + num + sd + "成功"
                            else:
                                result = "ｺﾛｺﾛ……" + num + sd + "失敗"
                    except:
                        result = "ｺﾛｺﾛ……" + num
                    l.append(result)
                    n.append(int(num))
                    x += int(num)
                if ad != "":
                    x += int(ad)
                if int(m[0]) != 1:
                    result = str(n) + str(ad) + " = " + str(x)
                    l.append(result)
                print(l)
                result = '\n'.join(l)
                if len(result) > 400:
                    result = "文字数制限……"
        except:
            traceback.print_exc()
            result = "エラーが出ました……"
        return result

    def omikuji(status):
        account=status["account"]
        content = Re1.text(status["content"])
        in_reply_to_id = None
        if re.compile('こおり(.*)みくじ(.*)(おねが(.*)い|お願(.*)い|[引ひ]([きく]|いて)|や[りる]|ください|ちょうだい|(宜|よろ)しく|ひとつ|し(て|たい))').search(content):
            if account['acct'] != "1":
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
                try:
                    with codecs.open('dic_time\\' + account["acct"] + '.json', 'r', 'UTF-8') as f:
                        if not f == "":
                            nstr = json.load(f)
                    last_time = datetime.strptime(re.sub("T..:..:..\....Z", "", nstr["omikuji_time"]), '%Y-%m-%d')
                    now_time = datetime.strptime(re.sub("T..:..:..\....Z", "", status['created_at']), '%Y-%m-%d')
                    if last_time != now_time:
                        print("◇Hit_try")
                        post = bot.rand_w('game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
                        c = {}
                        c.update({"omikuji_time":str(status["created_at"])})
                        w = nstr["omikuji_lack"]
                        n1 = order(w)
                        z = re.search("【(.+)】", post)
                        c.update({"omikuji_lack":z.group(1)})
                        n2 = order(z.group(1))
                        if n2 == 6:
                            post = post + "\n大吉です、おめでとうございます。"
                        elif n2 == -5:
                            post = post + "\n……ご愁傷様です。元気だしてくださいね。"
                        elif n1 < n2:
                            post = post + "\n前回より運気が上がりましたね。"
                        elif  n1 > n2:
                            post = post + "\n前回より運気が下がりましたね。"
                        elif n1 == n2:
                            post = post + "\n前回と同じ結果になりましたね。"
                        bot.toot_res(post, "public", sec=6)
                        with codecs.open('dic_time\\' + account["acct"] + '.json', 'w+', 'UTF-8') as f:
                            json.dump(c, f)
                        with codecs.open('dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'r', 'UTF-8') as f:
                            a = {}
                            a = json.load(f)
                        with codecs.open('dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                            a.update({re.sub("T..:..:..\....Z", "", status['created_at']): order(z.group(1))})
                            json.dump(a, f)
                    else:
                        s = "\n本日あなたが引いた結果は【{}】です。".format(nstr["omikuji_lack"])
                        bot.toot_res("@" + account['acct'] + " 一日一回ですよ！\n朝9時頃を越えたらもう一度お願いします！" + s,
                                     "public", status["id"], sec=3)
                except FileNotFoundError:
                    print("◇hit_New")
                    post = bot.rand_w('game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
                    bot.toot_res(post, "public", sec=6)
                    c = {}
                    c.update({"omikuji_time":str(status["created_at"])})
                    z = re.search("【(.+)】", post)
                    c.update({"omikuji_lack":z.group(1)})
                    with codecs.open('dic_time\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                        json.dump(c, f)
                    with codecs.open('dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                        a = {}
                        a.update({re.sub("T..:..:..\....Z", "", status['created_at']): order(z.group(1))})
                        json.dump(a, f)
                except json.decoder.JSONDecodeError:
                    print(traceback.format_exc())
                    print("◇hit_ReNew")
                    post = bot.rand_w('game\\' + 'kuji' + '.txt') + " " + "@" + account['acct'] + " #こおりみくじ"
                    bot.toot_res(post, "public", sec=6)
                    c = {}
                    c.update({"omikuji_time":str(status["created_at"])})
                    z = re.search("【(.+)】", post)
                    c.update({"omikuji_lack":z.group(1)})
                    with codecs.open('dic_time\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                        json.dump(c, f)
                    with codecs.open('dic_time\\omikuji_diary\\' + account["acct"] + '.json', 'w', 'UTF-8') as f:
                        a = {}
                        a.update({re.sub("T..:..:..\....Z", "", status['created_at']): order(z.group(1))})
                        json.dump(a, f)
                except:
                    e_me()
        return

    def aram(status):
        content = Re1.text(status["content"])
        account = status['account']
        com = re.search("(アラーム|[Aa][Rr][Aa][Mm])(\d+)([秒分]?)", content)
        sec = int(com.group(2))
        clo = com.group(3)
        if clo == "分":
            sec = sec * 60
        else:
            pass
        print(str(sec))
        post = "@" + account["acct"] + " " + "指定した時間が来たのでお知らせします。"
        g_vis = status["visibility"]
        return post, sec

    def land(status):
        in_reply_to_id = None
        content = Re1.text(status["content"])
        if re.compile("(.+)(開園)$").search(content):
            print("◇Hit")
            acc = status['account']
            if acc['acct'] != "1":
                com = re.search("(.+)(開園)", content)
                post = re.sub('<span class="">', '', com.group(1)) + "閉園"
                ba = threading.Timer(5, bot.toot, [post, "public", None, None, None])
                ba.start()

    def bals(status):
        in_reply_to_id = None
        if re.compile("バルス|ﾊﾞﾙｽ|ばるす|BA(.?)RU(.?)SU").search(status['content']):
            print("◇Hit")
            acc = status['account']
            if acc['acct'] != "1":
                count.bals += 1
                f = codecs.open('game\\bals.txt', 'w', 'utf-8')
                f.write(str(count.bals))
                f.close
                post = "[large=2x][color=red]目がぁぁぁ、目がぁぁぁ！x" + str(count.bals) + "[/color][/large]"
                ba = threading.Timer(0, bot.toot, [post, "public", None, None, None])
                ba.start()

    def mental_healther(staus):
        pass


class Loading():
    def deco(func):
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            f = func(*args, **kwargs)
            res("Streaming開始です【{}】").format(f)

        return wrapper

    @deco
    def go_local():  # listenerオブジェクトには監視させるものを（続く）
        try:
            listener = Local()
            mastodon.local_stream(listener)
        except:
            print("【例外情報】\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write("\n\n【LOCAL_ERROR: " + str(jst_now) + "】\n")
                traceback.print_exc(file=f)
                f.write("\n")
            sleep(180)
            Loading.re_local()
            pass

    @deco
    def go_user():  # （続き）継承で組み込んだものを追加するようにします。
        try:
            listener = User()
            mastodon.user_stream(listener)
        except:
            print("【例外情報】\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write("\n\n【USER_ERROR: " + str(jst_now) + "】\n")
                traceback.print_exc(file=f)
                f.write("\n")
            sleep(180)
            Loading.re_user()
            pass

    def re_local():
        relogin()
        uuu = threading.Thread(target=Loading.go_local)
        uuu.start()
        uuu.join()
        bot.toot("@0 ローカル、読み込み直しました", "direct")

    def re_user():
        relogin()
        lll = threading.Thread(target=Loading.go_user)
        lll.start()
        lll.join()
        bot.toot("@0 ホーム及び通知、読み込み直しました。", "direct")


def reload():
    pass


def relogin():
    mastodon = Mastodon(
        client_id="cred.txt",
        access_token="auth.txt",
        api_base_url=url_ins)  # インスタンス
    print("こおり「再ログインします。」")


def logout():
    bot.toot("ログアウトします。\nおやすみなさいです。")
    sleep(1)
    sys.exit()


def e_me():
    bot.toot("@0 エラーが出たようです。\n" + traceback.format_exc(), "direct")
    bot.toot("エラーが出ました……")

def e_stream(tl):
        print("エラー情報【{}】\n".format(tl))
        with open('error.log', 'a') as f:
            jst_now = datetime.now(timezone('Asia/Tokyo'))
            f.write("\n\n【" + str(jst_now) + "】\n")
            traceback.print_exc(file=f)
            f.white("\n")


def stream_init():
    try:
        uuu = threading.Timer(0, Loading.go_local)
        lll = threading.Timer(0, Loading.go_user)
        uuu.start()
        lll.start()
    except:
        e_me()
        sleep(3)
        bot.toot("すみません、ログアウトするかもしれません。")


if __name__ == '__main__':  # ファイルから直接開いたら動くよ！
    api_Bot = open("api_Bot.txt").read()
    count()
    k = input("start: ")
    if k is "":
        bot.toot("ログインしました。")
    elif k is "2":
        bot.toot("再起動しました。")
    stream_init = stream_init()
    s = threading.Thread(target=stream_init)
    s.start()
    if k is "":
        back01()
    s.join()
    print('読み込み完了しました。')
