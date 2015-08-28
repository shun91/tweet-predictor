#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encode: utf-8
"""
Twitter API との通信を行う．
"""
import os
import sys
import re
import json
import tweepy
import logging
import time
from flask import session

# Consumer Key
CONSUMER_KEY = os.environ['CONSUMER_KEY']
# Consumer Secret
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
# Callback URL
CALLBACK_URL = os.environ['ROOT_URL']


class Twitter(object):

    """ Twitter API との通信を行うクラス． """

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET,
                                        CALLBACK_URL)

    def get_access_token(self, token, verifier):
        """ 認証済みユーザの access_token, screen_name を取得 """
        # access_token, screen_name を取得して返す．
        self.auth.request_token = token
        try:
            self.auth.get_access_token(verifier)
            screen_name = self.get_screen_name(
                self.auth.access_token, self.auth.access_token_secret)
            return (self.auth.access_token, self.auth.access_token_secret, screen_name)
        except tweepy.TweepError, e:
            logging.error('get_access_token: ' + str(e))
            return ('', '', '')

    def get_authorization_url(self):
        """ 認証用URLを取得して返す． """
        try:
            redirect_url = self.auth.get_authorization_url()
            session['request_token'] = self.auth.request_token
            return redirect_url
        except tweepy.TweepError, e:
            logging.error('get_authorization_url: ' + str(e))

    def get_screen_name(self, access_token, access_token_secret):
        """ access_token から screen_name を取得して返す． """
        self.auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(self.auth)
        return api.me()._json['screen_name']

    def get_user(self, screen_name, access_token, access_token_secret):
        """ ユーザ情報 (screen_name, name, プロフ画像) を返す． """
        self.auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(self.auth)
        user = api.get_user(screen_name)._json
        return (user['screen_name'], user['name'], user['profile_image_url_https'])

    def user_timeline_texts(self, screen_name, access_token, access_token_secret):
        """
        user_timeline の text のリストを返す．
        """
        try:
            start = time.time() # tweet 取得に制限時間を設ける
            self.auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(self.auth)
            timeline_texts = []
            for status in tweepy.Cursor(api.user_timeline, screen_name=screen_name, count=200).items():
                timeline_texts.append(status.text.encode('utf-8'))
                if time.time() - start > 20:  # 20s 経ったらそこまでのツイートを返す
                    break
            return timeline_texts
        except tweepy.TweepError, e:
            logging.error('user_timeline_texts: ' + str(e))
            return []

    def removed_texts(self, texts):
        """ text のリストを受け取り，余計な文字列を除去したリストを生成して返す． """
        remover = Remover()
        return map(remover.remove, texts)


class Remover(object):

    """ Tweetからリプライ(@***)，ハッシュタグ(#***)，URLを除去． """

    def __init__(self):
        self.ptn_reply = re.compile(
            '(@[a-z|A-Z|0-9|_]+)|((http|https):\/\/[-\w\.]+(:\d+)?(\/[^\s]*)?)|(?:^|[^ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９a-zA-Z0-9&_\/]+)[#＃]([ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９a-zA-Z0-9_]*[ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９a-zA-Z]+[ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９a-zA-Z0-9_]*)')

    def remove(self, text):
        return self.ptn_reply.sub(r'', text)
