# coding: utf-8
"""
Twitter Streaming APIで指定の(複数可)ハッシュタグを監視して条件を満たすツイートをDBに格納する
"""
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

import MySQLdb
import tweepy

from secret import conf

fmt = "%(asctime)s %(levelname)s %(funcName)s :%(message)s"
logging.basicConfig(level=logging.INFO, format=fmt, filename='log/stream_crawler.log')
logger = logging.getLogger(__name__)

dbparams = {"host": "localhost",
            "db": "senkyo",
            "user": "senkyo",
            "passwd": "senkyo",
            "charset": "utf8mb4"}

auth = tweepy.OAuthHandler(conf['CK'], conf['CS'])
auth.set_access_token(conf['AT'], conf['AS'])
api = tweepy.API(auth, wait_on_rate_limit=True)
idol_names = []


def set_all_idol_names_from_db():
    with MySQLdb.connect(**dbparams) as conn:
        conn.execute("select id, name from idols")
    rows = list(conn)
    return rows


def insert_db(status, mode, title, idol_id, idol, text=None):
    """
    :param object status: Tweepyのstatusオブジェクト
    :param int mode: 総選挙 or ボイスオーディション
    :param int title モバマス or デレステ
    :param int idol_id: アイドル名
    :param unicode text: ツイート本文を上書き指定したいときに指定すること
    :return: None
    """
    if text is None:
        text = status.text
    with MySQLdb.connect(**dbparams) as c:
        c.execute(
            "insert into cg9th (tweet_id, user_id, screen_name, name, text, source, source_url, idol_id, idol, mode, title) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
            status.id, status.user.id, status.user.screen_name, status.user.name, text, status.source, status.source_url, idol_id, idol, mode, title)
            )


def get_idol_from_text(text):
    for name in idol_names:
        if name[1] in text:
            return name[0], name[1]
    return None, None


def check_vote_mode(text):
    if "#第9回シンデレラガール総選挙" in text:
        return 0  # "9th"
    elif "#ボイスアイドルオーディション" in text:
        return 1  # "voice"
    else:
        return None


def check_title(text):
    if "【アイドルマスター シンデレラガールズ】で" in text:
        return 0  # "mobamas"
    elif "【アイドルマスター シンデレラガールズ　スターライトステージ】で" in text:
        return 1  # "deresute"
    else:
        return None


def get_tweet(status):
    extended = False
    if hasattr(status, "extended_tweet"):  # 140文字拡張ツイートであるか?
        extended = True
        text = status.extended_tweet["full_text"]  # その場合はfull_textを本文として扱う
    else:
        text = status.text

    mode = check_vote_mode(text)
    if mode is None:
        return
    title = check_title(text)
    if title is None:
        return
    idol_id, idol = get_idol_from_text(text)
    if idol_id is None:
        return

    insert_db(status, mode, title, idol_id, idol, text=text)
    logger.info("insert DB: %s, idol: %s, mode: %s" % (status.id_str, idol, str(mode)))


class PublicStreamListener(tweepy.StreamListener):
    def __init__(self):
        super(PublicStreamListener, self).__init__()

    def on_status(self, status):
        if hasattr(status, "retweeted_status"):
            return True  # リツイートのツイートは処理せずに抜ける
        get_tweet(status)
        return True

    def on_error(self, status_code):
        logger.info('An error has occured! Status code = %s' % status_code)
        return True

    def on_timeout(self):
        logger.info('Timeout...')
        return True


def commandline_arg(arg):
    if isinstance(arg, str):
        unicode_string = arg.decode(sys.getfilesystemencoding())
        return unicode_string
    else:
        return arg


def main():
    global idol_names
    idol_names = set_all_idol_names_from_db()
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--hashtag', type=commandline_arg,
                        help='監視するTwitterハッシュタグ',
                        default="#第9回シンデレラガール総選挙 #ボイスアイドルオーディション")
    args = parser.parse_args()

    tags = args.hashtag.split()  # タグはスペース区切りで複数渡せる(後段へはList型で渡す)
    publiclistener = PublicStreamListener()
    publicstream = tweepy.Stream(auth=api.auth, listener=publiclistener)
    publicstream.filter(track=tags)


if __name__ == '__main__':
    logger.info("Program Start.")
    main()
