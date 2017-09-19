# -*- coding: utf-8 -*-

from mastodon import *
import feedparser

"""
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
"""


url_ins = open("instance.txt").read()  # instanceのアドレスお願いね　例：https://knzk.me

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス


class test():
    def rss():
        RSS_URL = ""https://knzk.me/@0.atom"" #ここにRSSの.atom

        rss_dic = feedparser.parse(RSS_URL)

        print(rss_dic.feed.title)

        for entry in rss_dic.entries:
            title = entry.title
            link = entry.link
            print(link)
            print(title)　#一覧が見れるかテスト用プリント
            
        test.title = rss_dic.entries[0].title　#さ一番上の記事を取得して
        test.link = rss_dic.entries[0].link

    def main():
        test.rss()
        #    media_files = [mastodon.media_post(media, "image/jpeg") for media in ["test.jpg"]]
        toot_now = test.title+"\n"+test.link
        #    mastodon.status_post(status=toot_now, media_ids=media_files, visibility=unlisted)
        mastodon.status_post(status=toot_now, visibility="public", spoiler_text="テストします")　#spoiler_textはCWしたときのタイトル入力値です
        """visibility 	One of: public, unlisted, private, direct"""

if __name__ == '__main__':
    test.main()
