# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import re, sys, os, csv, json, codecs, io
import threading, requests, random
from datetime import datetime
from pytz import timezone
from xml.sax.saxutils import unescape as unesc
import warnings, traceback
import numpy as np
import bot as koori

"""
上記必要なものはpipしていってね！！！
多分Mastodon.pyとrequestsくらいかな？
reは正規表現検索用　sysとjsonは多分何かの基盤
threadingはマルチ稼働のため　csvはトゥート保管のデータ形式のため。
codecsは文字化け処理用。　randomは文字通りランダムにするためのもの。
osフォルダ参照用。tracebackはエラー報告のデバック用。
datetime, timezoneは時間記録用。
warningsは……分からん！！！！
今後入れる予定のモジュ「Numpy」
"""

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)
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
print("こおり「ログイン、完了しました」")


class Re1():  # Content整頓用関数
    def text(text):
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|<'
                       '/span>|</a>|<span class="[a-z-]+">', "", str(text)))


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

UT = koori.bot.notic(mastodon)
LT = koori.bot.TL(mastodon)

class User(StreamListener):  # ホームでフォローした人と通知を監視するStreamingAPIの継承クラスです。
    def on_notification(self, notification):  # 通知を監視します。
        #import bot as koori
        try:
            print(("===●user_on_notification{}●===").format(str(notification["type"])))
            status = notification["status"]

            print(notification["type"])
            if notification["type"] == "follow":  # 通知がフォローだった場合はフォロバします。
                print(account["display_name"])
                sleep(2)
                mastodon.account_follow(account["id"])
                print("◇フォローを返しました。")

            elif notification["type"] == "mention":  # 通知がリプだった場合です。
                log = threading.Thread(Log(status).read())
                log.run()
                sec, post, g_vis, in_reply_to_id, media_files, spoiler_text = UT.mention(
                    notification["status"])
                if post:
                    t = threading.Timer(sec, bot.toot, [post, g_vis, in_reply_to_id, media_files, spoiler_text])
                    t.start()

            elif notification["type"] == "favourite":  # 通知がニコられたときです。
                #UT.favourite(status)
                account = status["account"]
                print(account["display_name"])
                if account["acct"] == "Knzk":
                    count.knzk_fav += 1
                    print("神崎にふぁぼられた数:" + str(knzk_fav))
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

            else:
                pass

        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.white(jst_now)
                traceback.print_exc(file=f)
            pass
        print("   ")
        #del sys.modules['bot']
        pass

    def on_update(self, status):
        pass


class Local(StreamListener):  # ここではLTLを監視する継承クラスになります。
    def on_update(self, status):  # StreamingAPIがリアルタイムにトゥート情報を吐き出してくれます。
        #import bot as koori
        try:
            log = threading.Thread(Log(status).read())
            log.run()
            LT.Local(status)
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass
        print("   ")
        #del sys.modules['bot']
        pass

    def on_delete(self, status_id):  # トゥー消し警察の監視場になります。
        try:
            print("===×on_delete×===")
            print(status_id)
            print("   ")
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
        print("   ")
        pass


"""
「mastodon.」メソッドを下記の関数によって「ホーム」「連合」「ローカル」「指定のハッシュタグ」が選択できます
 user_stream, public_stream, local_stream, hashtag_stream(self, tag, listener, async=False)
StreamingAPIでトゥートを参照することによりAPIの節約ができます。是非活用していきましょう（*'∀'人）
"""


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

    def rets(self, sec, post, g_vis, med=None, rep=None, spo=None):
        t = threading.Timer(sec, bot.toot, [post, g_vis, rep, med, spo])
        t.start()

    def fav_now(status):  # ニコります
        fav = status["id"]
        mastodon.status_favourite(fav)
        print("◇Fav")

    def reb_now(status):  # ブーストします
        reb = status["id"]
        mastodon.status_reblog(reb)
        print("◇Reb")

    def time_res():  # クールタイムが終わる処理。
        count.toot_CT = False
        print("◇tootの準備ができました")

    def t_forget():  # 同じ内容を連投しないためのクールタイムです。
        count.learn_toot = ""
        print("◇前のトゥート内容を忘れました")

    def hit(self, text):
        if re.compile(text).search(self.content):
            if self.account["acct"] == "1":
                return True

    def response(func):
        import functools
        def wrapper(*args, **kwargs):
            status, text, post, g_vis = func(*args,**kwargs)
            if re.compile(text).search(status["content"]):
                print("○hitしました♪")
                t = threading.Timer(5, bot.toot, [post, g_vis])
                t.start()
        return wrapper


class count():
    knzk_fav = 0
    toot_CT = False
    learn_toot = ""
    twotwo = 0
    f = codecs.open('game\\bals.txt', 'r', 'utf-8')
    bals = f.read()
    bals = int(bals)
    f.close
    pass


class Loading():
    def go_local():  # listenerオブジェクトには監視させるものを（続く）
        try:
            listener = local()
            mastodon.local_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write(str(jst_now))
                traceback.print_exc(file=f)
            sleep(180)
            bot.t_local()
            pass

    def go_user():  # （続き）継承で組み込んだものを追加するようにします。
        try:
            listener = user()
            mastodon.user_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write(str(jst_now))
                traceback.print_exc(file=f)
            sleep(180)
            bot.t_user()
            pass

    def re_local():
        uuu = threading.Thread(target=Loading.go_local)
        uuu.start()

    def re_user():
        lll = threading.Thread(target=Loading.go_user)
        lll.start()


def reload():
    pass


def relogin():
    mastodon = Mastodon(
        client_id="cred.txt",
        access_token="auth.txt",
        api_base_url=url_ins)  # インスタンス
    print("こおり「再ログインします。」")


if __name__ == '__main__':  # ファイルから直接開いたら動くよ！
    api_Bot = open("api_Bot.txt").read()
    count()
    bot.toot("ログインしました。テスト中です。")
    uuu = threading.Timer(0, Loading.go_local)
    uuu.start()
    lll = threading.Timer(0, Loading.go_user)
    lll.start()
    bot.toot("@0 読み込み、終了です。", "direct")
    uuu.join()
    lll.join()
    bot.toot("すみません、寝落ちするかもしれません。")
