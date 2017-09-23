# -*- coding: utf-8 -*-

from mastodon import *
import codecs
import sys
import tkinter as Tk


url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス


def Post(event):
    post_toot = EditBox.get(0.0, Tk.END)
    toot(post_toot)
    EditBox.delete(0.0, Tk.END)

def toot(post_toot, g_vis="public", in_reply_to_id=None, media_files=None, spoiler_text=None):  # トゥートする関数処理だよ！
    if val.get() == 0:
        g_vis="public"
    elif val.get() == 1:
        g_vis="unlisted"
    elif val.get() == 2:
        g_vis="private"
    elif val.get() == 3:
        g_vis="direct"
    in_reply_to_id=Reply.get()
    mastodon.status_post(status=post_toot, visibility=g_vis, in_reply_to_id=in_reply_to_id, media_ids=media_files, spoiler_text=spoiler_text)

root = Tk.Tk()
root.title(u"こおり_tootする装置")
root.geometry("220x460")
# ボタンが押されるとここが呼び出される
#テキスト
EditBox = Tk.Text(width=50)
EditBox.pack()

#公開範囲

val = Tk.IntVar()
val.set(0)

r0 = Tk.Radiobutton(text = u"公開", variable = val, value = 0)
r0.pack()
r1 = Tk.Radiobutton(text = u"未収載", variable = val, value = 1)
r1.pack()
r2 = Tk.Radiobutton(text = u"非公開", variable = val, value = 2)
r2.pack()
r3 = Tk.Radiobutton(text = u"ダイレクト", variable = val, value = 3)
r3.pack()

Reply = Tk.Entry()
Reply.pack()

#ボタン
Button = Tk.Button(text=u'Toot', width=50)
Button.bind("<Button-1>",Post) 
#左クリック（<Button-1>）されると，DeleteEntryValue関数を呼び出すようにバインド
Button.pack()

if __name__ == '__main__':
    root.mainloop()


