# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import re, sys, os, csv, json, codecs, io
import threading, requests, random
from datetime import datetime
from pytz import timezone
from xml.sax.saxutils import unescape as unesc
import warnings, traceback


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

"""
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)
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


class User(StreamListener):  # ホームでフォローした人と通知を監視するStreamingAPIの継承クラスです。
    def on_notification(self, notification):  # 通知を監視します。
        import bot as koori
        try:
            print(("===●user_on_notification{}●===").format(str(notification["type"])))
            status = notification["status"]

            print(notification["type"])
            if notification["type"] == "follow":  # 通知がフォローだった場合はフォロバします。
                sleep(2)
                mastodon.account_follow(account["id"])
                print("◇フォローを返しました。")

            elif notification["type"] == "mention":  # 通知がリプだった場合です。
                log = threading.Thread(Log(status).read())
                log.run()
                sec, post_toot, g_vis, in_reply_to_id, media_files, spoiler_text = koori.bot.mention(
                    notification["status"])
                if post_toot:
                    t = threading.Timer(sec, bot.toot, [post_toot, g_vis, in_reply_to_id, media_files, spoiler_text])
                    t.start()

            elif notification["type"] == "favourite":  # 通知がニコられたときです。
                koori.bot.favourite(status)

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
        del sys.modules['bot']
        pass


class Local(StreamListener):  # ここではLTLを監視する継承クラスになります。
    def on_update(self, status):  # StreamingAPIがリアルタイムにトゥート情報を吐き出してくれます。
        import bot as koori
        try:
            log = threading.Thread(Log(status).read())
            log.run()
            global mastodon
            koori.LTL(status, mastodon)
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass
        print("   ")
        del sys.modules['bot']
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


class bot():
    def __init__(self):
        self.in_reply_to_id = None
        self.media_files = None

    def toot(post_toot, g_vis="public", in_reply_to_id=None, media_files=None, spoiler_text=None):  # トゥートする関数処理だよ！
        print(in_reply_to_id)
        mastodon.status_post(status=post_toot, visibility=g_vis, in_reply_to_id=in_reply_to_id, media_ids=media_files,
                             spoiler_text=spoiler_text)

    def rets(self, sec, post_toot, g_vis, med=None, rep=None, spo=None):
        t = threading.Timer(sec, bot.toot, [post_toot, g_vis, rep, med, spo])
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

    def t_local():  # listenerオブジェクトには監視させるものを（続く）
        try:
            listener = Local()
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

    def t_user():  # （続き）継承で組み込んだものを追加するようにします。
        try:
            listener = User()
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


def reload():
    pass


if __name__ == '__main__':  # ファイルから直接開いたら動くよ！
    api_Bot = open("api_Bot.txt").read()
    count()
    uuu = threading.Thread(target=bot.t_local)
    uuu.start()
    lll = threading.Thread(target=bot.t_user)
    lll.start()
