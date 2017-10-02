# -*- coding: utf-8 -*-

from mastodon import *
import codecs
import sys
import tkinter as Tk
import tkinter.filedialog as Filed
import re

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

class temp():
    def _init_(self):
        self.filename = None

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
    if  temp.filename != None:
        xxx = re.sub("(.*)\.", "", temp.filename)
        media_files = [mastodon.media_post(temp.filename, "image/" + xxx)]
    mastodon.status_post(status=post_toot, visibility=g_vis, in_reply_to_id=in_reply_to_id, media_ids=media_files, spoiler_text=spoiler_text)
    echo.set("None")
    temp.filename = None

def file(event):
    temp.filename = Filed.askopenfilename()
    echo.set(str(temp.filename))
    return temp.filename

root = Tk.Tk()
root.title(u"こおり_tootする装置")
root.geometry("220x600")
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
Media = Tk.Button(text=u'メディア添付', width=50)
Media.bind("<Button-1>",file) 
#左クリック（<Button-1>）
Media.pack()

echo = Tk.StringVar()
Static1 = Tk.Label(textvariable=echo)
Static1.pack()
echo.set(u'None')

#ボタン
Button = Tk.Button(text=u'Toot', width=50)
Button.bind("<Button-1>",Post) 
Button.pack()

if __name__ == '__main__':
    temp.filename = None
    root.mainloop()


