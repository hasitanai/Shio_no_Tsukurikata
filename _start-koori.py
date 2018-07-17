from mastodon import *
import os, warnings, sys
print (__name__)

# こおりちゃん本体です（予定）
"""
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                                  encoding=sys.stdout.encoding,
                                  errors='backslashreplace',
                                  line_buffering=sys.stdout.line_buffering)
    warnings.simplefilter("ignore", UnicodeWarning)
"""

# ログイントークン取得済みで動かしてね（*'∀'人）
# 自分はこちらの記事を参照しましたのでアクセストークン各自で取ってね(*'ω'*)
# https://routecompass.net/mastodon/


if __name__ == '__main__':  # ファイルから直接開いたら動くよ！
    url_ins = open("login\\instance.txt").read()
    # instanceのアドレス　例：https://knzk.me
    mastodon = Mastodon(
        client_id="login\\cred.txt",
        access_token="login\\auth.txt",
        api_base_url=url_ins)  # インスタンス
    k = input("start: ")
    import bot
    bot.stream.main(mastodon,k)
    print("こおり「ログイン、完了しました」")