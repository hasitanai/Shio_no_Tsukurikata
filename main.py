# -*- coding: utf-8 -*-

from mastodon import *
from time import sleep
import feedparser
import re, sys, os, csv, json, codecs
import threading, requests, random
from datetime import datetime
from pytz import timezone
import warnings, traceback

import kooribot as koori

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
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|</span>|</a>|<span class="[a-z-]+">',
                       "",str(text)))


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
                sec, post_toot, g_vis, in_reply_to_id = koori.mention(notification["status"])
                t = threading.Timer(sec, bot.toot, [post_toot, g_vis, in_reply_to_id, None, None])
                t.start()

            elif notification["type"] == "favourite":  # 通知がニコられたときです。
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
                        post_toot = (l[s - 1])
                        g_vis = "public"
                        bot.toot_res(post_toot, g_vis)
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
        pass


class local_res_toot(StreamListener):  # ここではLTLを監視する継承クラスになります。
    def on_update(self, status):  # StreamingAPIがリアルタイムにトゥート情報を吐き出してくれます。
        try:
            print("===○local_on_update○===")
            account = status["account"]
            mentions = Re1.text(status["mentions"])
            content = Re1.text(status["content"])
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            print((re.sub("<p>|</p>", "",
                          str(account["display_name"]).translate(non_bmp_map) + "@" + str(account["acct"]).translate(
                              non_bmp_map))))
            print(content.translate(non_bmp_map))
            print(mentions.translate(non_bmp_map))
            print("   ")
            global mastodon
            koori.LTL(status, mastodon)
            pass
        except Exception as e:
            print("エラー情報\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass
        print("   ")
        pass

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

    def rets(self, sec, post_toot, g_vis, med=None, rep=None, spo=None):
        t = threading.Timer(sec, bot.toot, [post_toot, g_vis, rep, med, spo])
        t.start()

    def toot_res(post_toot, g_vis, in_reply_to_id=None, media_files=None,
                  spoiler_text=None):  # Postする内容が決まったらtoot関数に渡します。
        # その後は直ぐに連投しないようにクールタイムを挟む処理をしてます。
        if count.learn_toot != post_toot:
            count.learn_toot = post_toot
            bot.rets(post_toot, g_vis, in_reply_to_id, media_files, spoiler_text)
            t = threading.Timer(2, bot.time_res)
            t.start()
            count.toot_CT = True
            z = threading.Timer(60, bot.t_forget)  # クールタイム伸ばした。
            z.start()

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
            listener = local_res_toot()
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
            listener = user_res_toot()
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


if __name__ == '__main__':  # ファイルから直接開いたら動くよ！
    api_Bot = open("api_Bot.txt").read()
    count()
    uuu = threading.Timer(0, bot.t_local)
    uuu.start()
    lll = threading.Timer(0, bot.t_user)
    lll.start()
