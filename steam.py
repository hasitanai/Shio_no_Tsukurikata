# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import warnings
import re
import sys
import threading
import requests
import json
import csv
import codecs
import random
from datetime import datetime
import os
import traceback

"""
上記必要なものはpipしていってね！！！
多分Mastodon.pyとrequestsくらいかな？
reは正規表現検索用　sysとjsonは多分何かの基盤
threadingはマルチ稼働のため　csvはトゥート保管のデータ形式のため。
codecsは文字化け処理用。　randomは文字通りランダムにするためのもの。
warningsは……分からん！！！！
今後入れる予定のモジュ「os」
"""

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


class user_res_toot(StreamListener):  # ホームでフォローした人と通知を監視するStreamingAPIの継承クラスです。
    def on_notification(self, notification):  # 通知を監視します。
        print("===●user_on_notification●===")
        account = notification["account"]
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        print((re.sub("<p>|</p>", "",
                      str(account["display_name"]).translate(non_bmp_map) + "@" + str(account["acct"]).translate(
                          non_bmp_map))))
        print(notification["type"])
        if notification["type"] == "follow":  # 通知がフォローだった場合はフォロバします。
            sleep(2)
            mastodon.account_follow(account["id"])
            print("◇フォローを返しました。")

        elif notification["type"] == "mention":  # 通知がリプだった場合です。
            status = notification["status"]
            account = status["account"]
            mentions = status["mentions"]
            content = status["content"]
            print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
            print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
            if re.compile("こおり(.*)(ネイティオ|ねいてぃお)(.*)鳴").search(status['content']):
                post_toot = "@" + str(account["acct"]) + " " + "ネイティオさん、私が起きてから" + str(count.twotwo) + "回鳴きました。"
                g_vis = status["visibility"]
            elif re.compile("トゥートゥートゥー？|ﾄｩｰﾄｩｰﾄｩｰ?").search(status['content']):
                post_toot = "@" + str(account["acct"]) + " " + "トゥートゥー、トゥートゥトゥトゥ「" + str(count.twotwo) + "」"
                g_vis = status["visibility"]
            elif re.compile("\d+[dD]\d+").search(status['content']):
                coro = (re.sub("<p>|</p>", "", str(status['content']).translate(non_bmp_map)))
                post_toot="@"+str(account["acct"])+"\n"+game.dice(coro)
                g_vis = status["visibility"]
            else:
                global api_Bot
                url = "https://chatbot-api.userlocal.jp/api/chat"  # 人工知能APIサービス登録してお借りしてます。
                s = requests.session()
                mes = (re.sub("<span class(.*)/a></span>|<p>|</p>", "", str(content)))
                params = {
                    'key': api_Bot,  # 登録するとAPIKeyがもらえますのでここに入れます。
                    'message': mes,
                }
                r = s.post(url, params=params)
                ans = json.loads(r.text)
                post_toot = "@" + str(account["acct"]) + " " + ans["result"]
                g_vis = status["visibility"]
            in_reply_to_id = status["id"]
            t = threading.Timer(5, bot.toot, [post_toot, g_vis, in_reply_to_id, None, None])
            t.start()

        elif notification["type"] == "favourite":  # 通知がニコられたときです。
            if account["acct"] == "knzk":
                bot.knzk_fav += 1
                print("神崎にふぁぼられた数:" + bot.knzk_fav)
                if bot.knzk_fav == 10:
                    f = codecs.open('res\\fav_knzk.txt', 'r', 'utf-8')
                    l = []
                    for x in f:
                        l.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(l)
                    s = random.randint(1, m)
                    post_toot = (l[s - 1])
                    bot.toot_res(post_toot)
        pass


class local_res_toot(StreamListener):  # ここではLTLを監視する継承クラスになります。
    def on_update(self, status):  # StreamingAPIがリアルタイムにトゥート情報を吐き出してくれます。
        print("===○local_on_update○===")
        account = status["account"]
        mentions = status["mentions"]
        content = status["content"]
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        print((re.sub("<p>|</p>", "",
                      str(account["display_name"]).translate(non_bmp_map) + "@" + str(account["acct"]).translate(
                          non_bmp_map))))
        print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
        print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
        print("   ")
        bot.check01(status)
        bot.fav01(status)
        bot.res01(status)
        bot.res02(status)  # ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
        bot.res03(status)  # もっとここは上手くスマートに出来ると思うけどゴリ押し（はぁと
        bot.res04(status)
        bot.res05(status)
        bot.res06(status)
        bot.check02(status)
        bot.check03(status)
        bot.twotwo(status)
        pass

    def on_delete(self, status_id):  # トゥー消し警察の監視場になります。
        print("===×on_delete×===")
        print(status_id)
        pass


class bot():
    def __init__(self):
        self.in_reply_to_id = None
        self.media_files = None

    def toot(post_toot, g_vis="public", in_reply_to_id=None, media_files=None, spoiler_text=None):  # トゥートする関数処理だよ！
        print(in_reply_to_id)
        mastodon.status_post(status=post_toot, visibility=g_vis, in_reply_to_id=in_reply_to_id, media_ids=media_files, spoiler_text=spoiler_text)

    def res01(status):  # お返事関数シンプル版。
        in_reply_to_id = None
        if count.timer_toot == 0:
            f = codecs.open('reply.csv', 'r', "UTF-8", "ignore")
            dataReader = csv.reader(f)
            for row in dataReader:
                if re.compile(row[2]).search(status['content']):
                    print("◇Hit")
                    acc = status['account']
                    if acc['acct'] != "1":
                        if re.compile("[0-9]").search(row[0]):
                            sleep(int(row[0]))
                        else:
                            sleep(4)
                        post_toot = row[1].replace('\\n', '\n')
                        bot.toot_res(post_toot, "public", None, None, None)

    def res02(status):  # 該当するセリフからランダムtootが選ばれてトゥートします。
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        in_reply_to_id = None
        if count.timer_toot == 0:
            f = codecs.open('reply_random.csv', 'r', "UTF-8", "ignore")
            dataReader = csv.reader(f)
            for row in dataReader:
                if re.compile(row[2]).search(re.sub("<p>|</p>", "", status['content'].translate(non_bmp_map))):
                    acc = status['account']
                    if acc['acct'] != "1":
                        print("◇Hit")
                        if re.compile("[0-9]").search(row[0]):
                            sleep(int(row[0]))
                        else:
                            sleep(4)
                        post_toot = bot.rand_w('res\\' + row[1] + '.txt')
                        bot.toot_res(post_toot, "public", None, None, None)
                    return

    def res03(status):  # 該当する文字があるとメディアをアップロードしてトゥートしてくれます。
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        in_reply_to_id = None
        if count.timer_toot == 0:
            f = codecs.open('reply_media.csv', 'r', "UTF-8", "ignore")
            dataReader = csv.reader(f)
            for row in dataReader:
                if re.compile(row[2]).search(re.sub("<p>|</p>", "", status['content'].translate(non_bmp_map))):
                    acc = status['account']
                    if acc['acct'] != "1":
                        print("◇Hit")
                        if re.compile("[0-9]").search(row[0]):
                            sleep(int(row[0]))
                        else:
                            sleep(4)
                            f = codecs.open(txt_deta, 'r', 'utf-8')
                        l = []
                        for x in f:
                            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
                        f.close()
                        m = len(l)
                        s = random.randint(1, m)
                        post_toot = bot.rand_w('res\\' + row[1] + '.txt')
                        f = codecs.open('res_med\\' + row[3] + '.txt', 'r', 'utf-8')
                        j = []
                        for x in f:
                            j.append(x.rstrip("\r\n").replace('\\n', '\n'))
                        f.close()
                        xxx = re.sub("(.*)\.", "", j[s])
                        media_files = [mastodon.media_post("media\\" + j[s - 1], "image/" + xxx)]
                        print("◇メディア選択しました")
                        bot.toot_res(post_toot, "public", None, media_files, None)
                    return

    def res04(status):  # おはよう機能
        account = status["account"]
        if account["acct"] != "1":  # 一人遊びで挨拶しないようにするための処置
            try:
                f = codecs.open('oyasumi\\' + account["acct"] + '.txt', 'r', 'UTF-8')
                zzz = f.read()
                f.close()  # ファイルを閉じる
                if zzz == "good_night":
                    print("◇Hit")
                    post_toot = account['display_name'] + "さん\n" + rand_w('time\\oha.txt')
                    g_vis = "public"
                    t1 = threading.Timer(8, bot.toot[post_toot, "public", None, None, None])
                    t1.start()
                elif zzz == "active":
                    f = codecs.open('at_time\\' + account["acct"] + '.txt', 'r', 'UTF-8')
                    nstr = f.read()
                    f.close
                    tstr = re.sub("\....Z", "", nstr)
                    last_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                    nstr = status['created_at']
                    tstr = re.sub("\....Z", "", nstr)
                    now_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                    delta = now_time - last_time
                    if delta >= 10800:
                        if now_time.hour in range(3, 9):
                            to_r = bot.rand_w('time\\kon.txt')
                        elif now_time.hour in range(9, 20):
                            to_r = bot.rand_w('time\\kob.txt')
                        else:
                            to_r = bot.rand_w('time\\oha.txt')
                        print("◇Hit")
                        post_toot = account['display_name'] + "さん\n" + to_r
                        g_vis = "public"
                        t1 = threading.Timer(3, bot.toot, [post_toot, "public", None, None, None])
                        t1.start()
                else:
                    print("◇Hit")
                    post_toot = account['display_name'] + "さん\n" + "はじめまして、よろしくお願いいたします。"
                    g_vis = "public"
                    t1 = threading.Timer(5, bot.toot, [post_toot, "public", None, None, None])
                    t1.start()
            except:
                f = codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8')
                f.write("active")
                f.close()

    def res05(status):  # おやすみ機能
        account = status["account"]
        if account["acct"] != "1":  # 一人遊びで挨拶しないようにっするための処置
            if re.compile("寝マストドン|寝ます|みんな(.*)おやすみ|おやすみ(.*)みんな").search(status['content']):
                print("◇Hit")
                post_toot = account['display_name'] + "さん\n" + rand_w('time\\oya.txt')
                t1 = threading.Timer(3, toot, [post_toot, "public", None, None, None])
                t1.start()
            elif re.compile("こおり(.*)おやすみ").search(status['content']):
                print("◇Hit")
                post_toot = account['display_name'] + "さん\n" + rand_w('time\\oya.txt')
                t1 = threading.Timer(5, bot.toot, [post_toot, "public", None, None, None])
                t1.start()

    def res06(status):
        if re.compile("こおり(.*)[1-5][dD]\d+").search(status['content']):
            print("○hitしました♪")
            account = status["account"]
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            coro = (re.sub("<p>|</p>", "", str(status['content']).translate(non_bmp_map)))
            post_toot="@"+str(account["acct"])+"\n"+game.dice(coro)
            g_vis = status["visibility"]
            t = threading.Timer(5, bot.toot, [post_toot, g_vis, None, None, "サイコロ振りますね。"])
            t.start()

    def fav01(status):  # 自分の名前があったらニコブーして、神崎があったらニコります。
        if re.compile("こおり|(神[埼崎]|knzk|(100|5000兆)db)").search(status['content']):
            v = threading.Timer(1, bot.fav_now, [status])
            v.start()


        if re.compile("こおり").search(status['content']):
            b = threading.Timer(2, bot.reb_now, [status])
            b.start()

    def fav_now(status):  # ニコります
        fav = status["id"]
        mastodon.status_favourite(fav)
        print("◇Fav")

    def reb_now(status):  # ブーストします
        reb = status["id"]
        mastodon.status_reblog(reb)
        print("◇Reb")

    def toot_res(post_toot, g_vis, in_reply_to_id=None,
                 media_files=None):  # Postする内容が決まったらtoot関数に渡します。その後は直ぐに連投しないようにクールタイムを挟む処理をしてます。
        g_vis = g_vis
        in_reply_to_id = in_reply_to_id
        media_files = media_files
        if count.learn_toot != post_toot:
            count.learn_toot = post_toot
            bot.toot(post_toot, g_vis, in_reply_to_id, media_files)
            t = threading.Timer(10, bot.time_res)
            t.start()
            count.timer_toot = 1
            z = threading.Timer(180, bot.t_forget)  # クールタイム伸ばした。
            z.start()

    def check01(status):  # アカウント情報の更新
        account = status["account"]
        created_at = status['created_at']
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        f = codecs.open('acct\\' + account["acct"] + '.txt', 'w', 'UTF-8')
        f.write(str(status["account"]).translate(non_bmp_map))
        f.close()

    def check02(status):  # 最後にトゥートした時間の記憶
        account = status["account"]
        created_at = status['created_at']
        f = codecs.open('at_time\\' + account["acct"] + '.txt', 'w', 'UTF-8')
        f.write(str(status["created_at"]))  # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z
        f.close()  # ファイルを閉じる
        f = codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8')
        f.write("active")  #
        f.close()  # ファイルを閉じる

    def check03(status):  # お休みした人を記憶する
        account = status["account"]
        if re.compile("寝マストドン|寝ます|みんな(.*)おやすみ|おやすみ(.*)みんな").search(re.sub("<p>|</p>", "", status['content'])):
            f = codecs.open('oyasumi\\' + account["acct"] + '.txt', 'w', 'UTF-8')
            f.write("good_night")  #
            f.close()  # ファイルを閉じる
            print("◇寝る人を記憶しました")

    def twotwo(status):  # ネイティオが鳴いた数を監視しまーすｗｗｗｗｗ
        account = status["account"]
        if account["acct"] == "twotwo":
            if re.compile("トゥ|ﾄｩ").search(re.sub("<p>|</p>", "", status['content'])):
                count.twotwo += 1
                print("ネイティオが鳴いた数:" + str(count.twotwo))

    def rand_w(txt_deta):
        f = codecs.open(txt_deta, 'r', 'utf-8')
        l = []
        for x in f:
            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
        f.close()
        m = len(l)
        s = random.randint(1, m)
        return l[s - 1]

    def time_res():  # クールタイムが終わる処理。
        count.timer_toot = 0
        print("◇tootの準備ができました")

    def t_local():  # listenerオブジェクトには監視させるものを（続く）
        listener = local_res_toot()
        mastodon.local_stream(listener)

    def t_user():  # （続き）継承で組み込んだものを追加するようにします。
        listener = user_res_toot()
        mastodon.user_stream(listener)

    def t_forget():  # 同じ内容を連投しないためのクールタイムです。
        bot.learn_toot = ""
        print("◇前のトゥート内容を忘れました")


class count():
    knzk_fav = 0
    timer_toot = 0
    learn_toot = ""
    twotwo = 0

class game():
    def dice(inp):
        l=[]
        n=[]
        x=0
        try:
            rr = re.search("\d+[dD]", str(inp))
            r = re.sub("[dD]", "", str(rr.group()))
            if re.compile("(\d+)[:<>](\d+)").search(inp):
                ss = re.search("(.*)[dD](\d+)([:<>])(\d+)([^\d]*)", str(inp))
                print(str(ss.group(4)))
                s = str(ss.group(4))
                sd = str(ss.group(4))
            m = re.search("[dD](\d+)", str(inp))
            m = re.sub("[dD]", "", str(m.group(1)))
            m = int(m)
            r = int(r)
            if m == 0:
                result = "面がないので振りません"
            elif r >= 51:
                result = "回数が多いので振りません"
            elif r == 0:
                result = "回数0なので振りません"
            else:
                print(str(m),str(r))
                print("○サイコロ振ります")
                for var in range(0, r):
                    num = random.randint(1, m)
                    num = str(num)
                    try:
                        if str(ss.group(3)) == ">":
                            if int(num) >= int(s):
                                result="ｺﾛｺﾛ……"+num+":成功 "+sd
                            else:
                                result="ｺﾛｺﾛ……"+num+":失敗 "+sd
                        else:
                            if int(num) <= int(s):
                                result="ｺﾛｺﾛ……"+num+":成功 "+sd
                            else:
                                result="ｺﾛｺﾛ……"+num+":失敗 "+sd
                    except:
                        result="ｺﾛｺﾛ……"+num
                    l.append(result)
                    n.append(int(num))
                    x += int(num)
                if r != 1:
                    result=str(n)+" = "+str(x)
                    l.append(result)
                print(l)
                result = '\n'.join(l)
                if len(result) > 400:
                    result = "文字数制限……"
        except:
            traceback.print_exc()
            result="エラーが出ました……"
        return result

if __name__ == '__main__':  # ファイルから直接開いたら動くよ！
    api_Bot = open("api_Bot.txt").read()
    count()
    u = threading.Timer(0, bot.t_local)
    u.start()
    l = threading.Timer(0, bot.t_user)
    l.start()

"""
「mastodon.」メソッドを下記の関数によって「ホーム」「連合」「ローカル」「指定のハッシュタグ」が選択できます
 user_stream, public_stream, local_stream, hashtag_stream(self, tag, listener, async=False)

現在、絵文字コードの文字化けが解決してません……なので表示しないように処理をしています。
StreamingAPIでトゥートを参照することによりAPIの節約ができます。是非活用していきましょう（*'∀'人）

コードの整頓で見事、綺麗になりました。
今後は機械学習を導入する予定です。
"""
