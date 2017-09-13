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

"""
上記必要なものはpipしていってね！！！
多分Mastodon.pyとrequestsくらいかな？
reは正規表現検索用　sysとjsonは多分何かの基盤
threadingはマルチ稼働のため　csvはトゥート保管のデータ形式のため。
codecsは文字化け処理用。　randomは文字通りランダムにするためのもの。
warningsは……分からん！！！！
後々挨拶用の関数処理がほしいのでtime系列は増える予定です。
"""

warnings.simplefilter("ignore", UnicodeWarning)

"""
ログイントークン取得済みで動かしてね（*'∀'人）
自分はこちらの記事を参照しましたのでアクセストークン各自で取ってね(*'ω'*)
https://routecompass.net/mastodon/
"""
url_ins = open("instance.txt").read()

mastodon = Mastodon(
        client_id="cred.txt",
        access_token="auth.txt",
        api_base_url = url_ins) #インスタンス


class user_res_toot(StreamListener): #ホームでフォローした人と通知を監視するStreamingAPIの継承クラスです。
    def on_notification(self, notification): #通知を監視します。
        print("===●user_on_notification●===")
        account  = notification["account"]
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        print((re.sub("<p>|</p>", "", str(account["display_name"]).translate(non_bmp_map)+ "@" + str(account["acct"]).translate(non_bmp_map))))
        print(notification["type"])
        if notification["type"] == "follow": #通知がフォローだった場合はフォロバします。
            sleep(2)
            mastodon.account_follow(account["id"])
            print("◇フォローを返しました。")

        elif notification["type"] == "mention": #通知がリプだった場合です。
            status = notification["status"]
            account = status["account"]
            mentions = status["mentions"]
            content = status["content"]
            print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
            print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
            if mentions:
                m = mentions[0]
                print(m["acct"])
                if m["acct"] == "1":
                    global post_toot
                    global g_vis
                    global in_reply_to_id
                    url = "https://chatbot-api.userlocal.jp/api/chat" #人工知能APIサービス登録してお借りしてます。
                    s = requests.session()
                    mes = (re.sub("<span class(.*)/a></span>|<p>|</p>", "", str(content)))
                    params = {
                        'key': 'Sample', #登録するとAPIKeyがもらえますのでここに入れます。
                        'message': mes,
                    }
                    r =  s.post(url, params=params)
                    ans = json.loads(r.text)
                    post_toot = "@"+str(account["acct"])+" "+ans["result"]
                    g_vis = "unlisted"
                    in_reply_to_id = int(status["id"])
                    t = threading.Timer(5 ,toot)
                    t.start()

        elif notification["type"] == "favourite": #通知がニコられたときです。
            if account["acct"] == "knzk":
                global knzk_fav
                knzk_fav += 1
                print("神崎にふぁぼられた数:"+knzk_fav)
                if knzk_fav == 10:
                    f = codecs.open('res\\fav_knzk.txt', 'r', 'utf-8')
                    l = []
                    for x in f:
                        l.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(l)
                    s =random.randint(1,m)
                    post_toot = (l[s-1])
                    toot_res()
        pass

class local_res_toot(StreamListener): #ここではLTLを監視する継承クラスになります。
    def on_update(self, status): #StreamingAPIがリアルタイムにトゥート情報を吐き出してくれます。
        global g_sta
        print("===○local_on_update○===")
        account = status["account"]
        mentions = status["mentions"]
        content = status["content"]
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        print((re.sub("<p>|</p>", "", str(account["display_name"]).translate(non_bmp_map)+ "@" + str(account["acct"]).translate(non_bmp_map))))
        print((re.sub("<p>|</p>", "", str(content).translate(non_bmp_map))))
        print((re.sub("<p>|</p>", "", str(mentions).translate(non_bmp_map))))
        print("   ")
        g_sta = status
        res01()
        res02() #ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
        res03() #もっとここは上手くスマートに出来ると思うけどゴリ押し（はぁと
        fav01()
        pass

    def on_delete(self, status_id): #トゥー消し警察の監視場になります。
        print("===×on_delete×===")
        print(status_id)
        pass

def toot(): # トゥートする関数処理だよ！
    global post_toot
    global in_reply_to_id
    global media_files
    print(in_reply_to_id)
    mastodon.status_post(status=post_toot, visibility=g_vis, in_reply_to_id=in_reply_to_id,media_ids=media_files)

def res01(): #お返事関数シンプル版。
    global timer_toot
    global g_sta
    global post_toot
    global learn_toot
    global in_reply_to_id
    status = g_sta
    in_reply_to_id = None
    if timer_toot == 0:
        f = open('reply.csv', 'r')
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
                    toot_res()

def res02(): #該当するセリフからランダムtootが選ばれてトゥートします。
    global timer_toot
    global g_sta
    global post_toot
    global learn_toot
    global in_reply_to_id
    global media_files
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    status = g_sta
    in_reply_to_id = None
    if timer_toot == 0:
        f = open('reply_random.csv', 'r')
        dataReader = csv.reader(f)
        for row in dataReader:
            if re.compile(row[2]).search(re.sub("<p>|</p>","",status['content'].translate(non_bmp_map))):
                acc = status['account']
                if acc['acct'] != "1":
                    print("◇Hit")
                    if re.compile("[0-9]").search(row[0]):
                        sleep(int(row[0]))
                    else:
                        sleep(4)
                    f = codecs.open('res\\'+row[1]+'.txt', 'r', 'utf-8')
                    l = []
                    for x in f:
                        l.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(l)
                    s =random.randint(1,m)
                    post_toot = (l[s-1])
                    toot_res()
                return

def res03(): #該当する文字があるとメディアをアップロードしてトゥートしてくれます。
    global timer_toot
    global g_sta
    global post_toot
    global learn_toot
    global in_reply_to_id
    global media_files
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    status = g_sta
    in_reply_to_id = None
    if timer_toot == 0:
        f = open('reply_media.csv', 'r')
        dataReader = csv.reader(f)
        for row in dataReader:
            if re.compile(row[2]).search(re.sub("<p>|</p>","",status['content'].translate(non_bmp_map))):
                acc = status['account']
                if acc['acct'] != "1":
                    print("◇Hit")
                    if re.compile("[0-9]").search(row[0]):
                        sleep(int(row[0]))
                    else:
                        sleep(4)
                    f = codecs.open('res\\'+row[1]+'.txt', 'r', 'utf-8')
                    l = []
                    for x in f:
                        l.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(l)
                    s =random.randint(1,m)
                    post_toot = (l[s-1])
                    f = codecs.open('res_med\\'+row[3]+'.txt', 'r', 'utf-8')
                    l = []
                    for x in f:
                        l.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    xxx = re.sub("(.*)\.","",l[s])
                    media_files = [mastodon.media_post("media\\"+l[s-1], "image/"+xxx)]
                    print("◇メディア選択しました")
                    toot_res()
                return

def fav01(): #自分の名前があったらニコブーして、神崎があったらニコります。
    global g_sta
    global n_sta
    status = g_sta
    if re.compile("こおり").search(status['content']):
        n_sta = status
        v = threading.Timer(1 ,fav_now)
        v.start()
        b = threading.Timer(2 ,reb_now)
        b.start()

    if re.compile("神崎").search(status['content']):
        n_sta = status
        v = threading.Timer(1 ,fav_now)
        v.start()

def fav_now(): #ニコります
    global n_sta
    fav = n_sta["id"]
    mastodon.status_favourite(fav)
    print("◇Fav")

def reb_now(): #ブーストします
    global n_sta
    reb = n_sta["id"]
    mastodon.status_reblog(reb)
    print("◇Reb")

def toot_res(): #Postする内容が決まったらtoot関数に渡します。その後は直ぐに連投しないようにクールタイムを挟む処理をしてます。
    global timer_toot
    global g_vis
    global learn_toot
    g_vis = "public"
    if learn_toot != post_toot:
        learn_toot = post_toot
        toot()
        t=threading.Timer(15,time_res)
        t.start()
        timer_toot = 1
        z=threading.Timer(60,t_forget)
        z.start()


def time_res(): #クールタイムが終わる処理。
    global timer_toot
    timer_toot = 0
    print("◇tootの準備ができました")

def t_local(): #listenerオブジェクトには監視させるものを（続く）
    listener = local_res_toot()
    mastodon.local_stream(listener)

def t_user(): #（続き）継承で組み込んだ追加するようにします。
    listener = user_res_toot()
    mastodon.user_stream(listener)

def t_forget(): #同じ内容を連投しないためのクールタイムです。
    global learn_toot
    learn_toot = ""
    print("◇前のトゥート内容を忘れました")

if __name__ == '__main__': #ファイルから直接開いたら動くよ！
    knzk_fav = 0
    timer_toot = 0
    learn_toot = ""
    in_reply_to_id = None
    media_files = None
    u = threading.Timer(0 ,t_local)
    l = threading.Timer(0 ,t_user)
    u.start()
    l.start()

"""
「mastodon.」メソッドを下記の関数によって「ホーム」「連合」「ローカル」「指定のハッシュタグ」が選択できます
 user_stream, public_stream, local_stream, hashtag_stream(self, tag, listener, async=False)

現在、絵文字コードの文字化けが解決してません……なので表示しないように処理をしています。
StreamingAPIでトゥートを参照することによりAPIの節約ができます。是非活用していきましょう（*'∀'人）

今後改善したいところ：
・global変数を駆使してるのでこれをオブジェクト保持で上手くアレコレしたい。
・新しく追加するのが面倒なので綺麗にかんりわけできるようになりたぁーい！！！！
"""
