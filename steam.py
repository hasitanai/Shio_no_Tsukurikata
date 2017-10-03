# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import warnings
import re, sys, os, csv, json, codecs
import threading, requests, random
import requests
from datetime import datetime
import traceback

"""
上記必要なものはpipしていってね！！！　多分Mastodon.pyとrequestsくらいかな？
reは正規表現検索用　sysとjsonは多分何かの基盤
threadingはマルチ稼働のため　csvはトゥート保管のデータ形式のため。
codecsは文字化け処理用。　randomは文字通りランダムにするためのもの。
osフォルダ参照用。tracebackはエラー報告のデバック用。warningsは……分からん！！！！
今後入れる予定のモジュ「Numpy」
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
        try:
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
                print((re.sub("<span class(.+)</span></a></span>|<p>|</p>", "", str(content).translate(non_bmp_map))))
                print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
                if re.compile("こおり(.*)(ネイティオ|ねいてぃお)(.*)鳴").search(status['content']):
                    post_toot = "@" + str(account["acct"]) + " " + "ネイティオさん、私が起きてから" + str(count.twotwo) + "回鳴きました。"
                    g_vis = status["visibility"]
                    sec = 5
                elif re.compile("トゥートゥートゥー？|ﾄｩｰﾄｩｰﾄｩｰ?").search(status['content']):
                    post_toot = "@" + str(account["acct"]) + " " + "トゥートゥー、トゥートゥトゥトゥ「" + str(count.twotwo) + "」"
                    g_vis = status["visibility"]
                    sec = 5
                elif re.compile("\d+[dD]\d+").search(status['content']):
                    coro = (
                        re.sub("<span class(.+)</span></a></span>|<p>|</p>", "",
                               str(status['content']).translate(non_bmp_map)))
                    post_toot = "@" + str(account["acct"]) + "\n" + game.dice(coro)
                    g_vis = status["visibility"]
                    sec = 5
                elif re.compile("(アラーム|[Aa][Rr][Aa][Mm])(\d+)").search(status['content']):
                    post_toot,sec = game.aram(status)
                    g_vis = status["visibility"]
                else:
                    global api_Bot
                    url = "https://chatbot-api.userlocal.jp/api/chat"  # 人工知能APIサービス登録してお借りしてます。
                    s = requests.session()
                    mes = (re.sub("<span class(.+)</span></a></span>|<p>|</p>", "", str(content)))
                    params = {
                        'key': api_Bot,  # 登録するとAPIKeyがもらえますのでここに入れます。
                        'message': mes,
                    }
                    r = s.post(url, params=params)
                    ans = json.loads(r.text)
                    post_toot = "@" + str(account["acct"]) + " " + ans["result"]
                    g_vis = status["visibility"]
                    sec = 5
                in_reply_to_id = status["id"]
                t = threading.Timer(sec, bot.toot, [post_toot, g_vis, in_reply_to_id, None, None])
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
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)

class local_res_toot(StreamListener):  # ここではLTLを監視する継承クラスになります。
    def on_update(self, status):  # StreamingAPIがリアルタイムにトゥート情報を吐き出してくれます。
        try:
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
            game.omikuji(status)
            game.land(status)
            bot.check02(status)
            bot.check03(status)
            bot.twotwo(status)
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
        

    def on_delete(self, status_id):  # トゥー消し警察の監視場になります。
        try:
            print("===×on_delete×===")
            print(status_id)
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)

class bot():
    def __init__(self):
        self.in_reply_to_id = None
        self.media_files = None

    def toot(post_toot, g_vis="public", in_reply_to_id=None, media_files=None, spoiler_text=None):  # トゥートする関数処理だよ！
        print(in_reply_to_id)
        mastodon.status_post(status=post_toot, visibility=g_vis, in_reply_to_id=in_reply_to_id, media_ids=media_files,
                             spoiler_text=spoiler_text)

    def res01(status):  # お返事関数シンプル版。
        in_reply_to_id = None
        if not count.toot_CT:
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
        if not count.toot_CT:
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
        if not count.toot_CT:
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
                        f = codecs.open('res\\' + row[1] + '.txt', 'r', 'utf-8')
                        for x in f:
                            l.append(x.rstrip("\r\n|\ufeff").replace('\\n', '\n'))
                        f.close()
                        m = len(l)
                        s = random.randint(1, m)
                        post_toot = l[s - 1]
                        f = codecs.open('res_med\\' + row[3] + '.txt', 'r', 'utf-8')
                        j = []
                        for x in f:
                            j.append(x.rstrip("\r\n").replace('\\n', '\n'))
                        f.close()
                        xxx = re.sub("(.*)\.", "", j[s - 1])
                        media_files = [mastodon.media_post("media\\" + j[s - 1], "image/" + xxx)]
                        print("◇メディア選択しました")
                        print(j[s - 1])
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
                    post_toot = account['display_name'] + "さん\n" + bot.rand_w('time\\oha.txt')
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
                post_toot = account['display_name'] + "さん\n" + bot.rand_w('time\\oya.txt')
                t1 = threading.Timer(3, toot, [post_toot, "public", None, None, None])
                t1.start()
            elif re.compile("こおり(.*)おやすみ").search(status['content']):
                print("◇Hit")
                post_toot = account['display_name'] + "さん\n" + bot.rand_w('time\\oya.txt')
                t1 = threading.Timer(5, bot.toot, [post_toot, "public", None, None, None])
                t1.start()

    def res06(status):
        if re.compile("こおり(.*)[1-5][dD]\d+").search(status['content']):
            print("○hitしました♪")
            account = status["account"]
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            coro = (re.sub("<p>|</p>", "", str(status['content']).translate(non_bmp_map)))
            post_toot = "@" + str(account["acct"]) + "\n" + game.dice(coro)
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
                 media_files=None, spoiler_text=None):  # Postする内容が決まったらtoot関数に渡します。その後は直ぐに連投しないようにクールタイムを挟む処理をしてます。
        g_vis = g_vis
        in_reply_to_id = in_reply_to_id
        media_files = media_files
        if count.learn_toot != post_toot:
            count.learn_toot = post_toot
            bot.toot(post_toot, g_vis, in_reply_to_id, media_files, spoiler_text)
            t = threading.Timer(10, bot.time_res)
            t.start()
            count.toot_CT = True
            z = threading.Timer(60, bot.t_forget)  # クールタイム伸ばした。
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
        count.toot_CT = False
        print("◇tootの準備ができました")

    def t_local():  # listenerオブジェクトには監視させるものを（続く）
        listener = local_res_toot()
        mastodon.local_stream(listener)

    def t_user():  # （続き）継承で組み込んだものを追加するようにします。
        listener = user_res_toot()
        mastodon.user_stream(listener)

    def t_forget():  # 同じ内容を連投しないためのクールタイムです。
        count.learn_toot = ""
        print("◇前のトゥート内容を忘れました")


class count():
    knzk_fav = 0
    toot_CT = False
    learn_toot = ""
    twotwo = 0
    f = codecs.open('game\\bals.txt', 'r', 'utf-8')
    bals = f.read()
    bals = int(bals)
    f.close

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
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        in_reply_to_id = None
        if not count.toot_CT:
            if re.compile('こおり(.*)おみくじ(.*)(おねが(.*)い|お願(.*)い|[引ひ][きく]|や[りる])').search(
                    re.sub("<p>|</p>", "", status['content'].translate(non_bmp_map))):
                acc = status['account']
                if acc['acct'] != "1":
                    print("◇Hit")
                    sleep(5)
                    post_toot = bot.rand_w('game\\' + 'kuji' + '.txt') + " " + "@" + acc['acct'] + " #こおりみくじ"
                    bot.toot(post_toot, "public", None, None, None)
                return

    def aram(status):
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        content = str(status['content']).translate(non_bmp_map)
        account=status['account']
        com = re.search("(アラーム|[Aa][Rr][Aa][Mm])(\d+)([秒分]?)", content)
        sec = int(com.group(2))
        clo = com.group(3)
        if clo == "分":
            sec = sec*60
        else:
            pass
        print(str(sec))
        post_toot = "@" + account["acct"] + " " + "指定した時間が来たのでお知らせします。"
        g_vis = status["visibility"]
        return post_toot, sec

    def land(status):
        in_reply_to_id = None
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        content = re.sub("<p>|</p>", "", status['content'].translate(non_bmp_map))
        if re.compile("(.+)(開園)$").search(content):
            print("◇Hit")
            acc = status['account']
            if acc['acct'] != "1":
                com = re.search("(.+)(開園)", content)
                post_toot = com.group(1)+"閉園"
                ba = threading.Timer(5, bot.toot, [post_toot,"public", None, None, None])
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
                post_toot = "[large=2x][color=red]目がぁぁぁ、目がぁぁぁ！x"+str(count.bals)+"[/color][/large]"
                ba = threading.Timer(0, bot.toot, [post_toot,"public", None, None, None])
                ba.start()
        

if __name__ == '__main__':  # ファイルから直接開いたら動くよ！
    api_Bot = open("api_Bot.txt").read()
    count()
    uuu = threading.Timer(0, bot.t_local)
    uuu.start()
    lll = threading.Timer(0, bot.t_user)
    lll.start()

"""
「mastodon.」メソッドを下記の関数によって「ホーム」「連合」「ローカル」「指定のハッシュタグ」が選択できます
 user_stream, public_stream, local_stream, hashtag_stream(self, tag, listener, async=False)

現在、絵文字コードの文字化けが解決してません……なので表示しないように処理をしています。
StreamingAPIでトゥートを参照することによりAPIの節約ができます。是非活用していきましょう（*'∀'人）

コードの整頓で見事、綺麗になりました。
今後は機械学習を導入する予定です。
"""
