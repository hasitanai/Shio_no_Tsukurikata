from mastodon import Mastodon
from time import time
import os, gc, threading

from bot import conv

class count():
    print(os.getcwd())
    CT = 0
    end = 0
    learn_toot = ""

count()

def __init__(self):
    self.status = status
    self.content = conv.text(status["content"])
    self.account = status["account"]
    self.g_vis = "public"
    self.in_reply_to_id = None
    self.media_files = None

def toot(mastodon, post, g_vis="public", in_reply_to_id=None,
         media_files=None, spoiler_text=None):  # トゥートする関数処理だよ！
    print(in_reply_to_id)
    mastodon.status_post(status=post,
                         visibility=g_vis,
                         in_reply_to_id=in_reply_to_id,
                         media_ids=media_files,
                         spoiler_text=spoiler_text)

def toot_res(mastodon, post="", g_vis="public", in_reply_to_id=None,
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
        t = threading.Timer(ing, toot, [mastodon, post, g_vis, in_reply_to_id, media_files, spoiler_text])
        t.start()
        print("【次までのロスタイム:" + str(count.end + sec) + "】")
        s = threading.Timer(ing, res, [sec])
        s.start()
        del t
        del s
        gc.collect()
        count.CT = time()
        count.end = ing
        z = threading.Timer(30, t_forget)  # クールタイム伸ばした。
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

def res(sec):
    count.end = count.end - sec
    if count.end < 0:
        count.end = 0

def t_forget():  # 同じ内容を連投しないためのクールタイムです。
    count.learn_toot = ""
    print("◇前のトゥート内容を忘れました")
