#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
n-gram の生成, Tweet の生成
"""
# n-Gram Language Model with Knerser-Ney Smoother
# This code is available under the MIT License.
# (c)2013 Nakatani Shuyo / Cybozu Labs Inc.
import numpy
import twitter_api
import json
from datetime import datetime
import pytz
import logging


# 文の先頭と終端を表す文字列
START = u"\u0001"
END = u"\u0002"
# n のデフォルト値
N_DEFAULT = 7
# discount のデフォルト値
DISCOUNT = 0.5


class NGram(dict):

    def __init__(self, N, depth=1):
        self.freq = 0
        self.N = N
        self.depth = depth

    def inc(self, v):
        if self.depth <= self.N:
            if v not in self:
                self[v] = NGram(self.N, self.depth + 1)
            self[v].freq += 1
            return self[v]

    def dump(self):
        if self.depth <= self.N:
            return "%d:{%s}" % (self.freq, ",".join("'%s':%s" % (k, d.dump()) for k, d in self.iteritems()))
        return "%d" % self.freq

    def probKN(self, D, given=""):
        assert D >= 0.0 and D <= 1.0
        if given == "":
            voca = self.keys()
            n = float(self.freq)
            return voca, [self[v].freq / n for v in voca]
        else:
            if len(given) >= self.N:
                given = given[-(self.N - 1):]
            voca, low_prob = self.probKN(D, given[1:])
            cur_ngram = self
            for v in given:
                if v not in cur_ngram:
                    return voca, low_prob
                cur_ngram = cur_ngram[v]
            g = 0.0  # for normalization
            freq = []
            for v in voca:
                c = cur_ngram[v].freq if v in cur_ngram else 0
                if c > D:
                    g += D
                    c -= D
                freq.append(c)
            n = float(cur_ngram.freq)
            return voca, [(c + g * lp) / n for c, lp in zip(freq, low_prob)]


class Generator(object):

    def __init__(self, ngram):
        self.ngram = ngram
        self.start()

    def start(self):
        self.pointers = []

    def inc(self, v):
        pointers = self.pointers + [self.ngram]
        self.pointers = [d.inc(v) for d in pointers if d != None]
        self.ngram.freq += 1

    def printAll(self):
        pointers = self.pointers + [self.ngram]
        for pointer in pointers:
            for a in pointer:
                print a  # error


def charNgram(gen, texts):
    """
    文字ngramの生成
    """
    for s in texts:
        s = s.strip()  # 空白の削除
        if len(s) == 0:
            continue
        s = unicode(s, 'utf-8')
        s = START + s + END
        gen.start()
        for c in s:
            gen.inc(c)


def predict(screen_name='ariyosihiroiki', n=N_DEFAULT, access_token='', access_token_secret=''):
    """ ユーザの過去のツイートから新たなツイートを生成する．json で返す． """
    # n が空文字列の場合の対処
    if (n == '') or (n is None):
        n = N_DEFAULT

    # ツイート生成に必要なインスタンス等
    numpy.random.seed()
    D = DISCOUNT # discount
    ngram = NGram(int(n))
    gen = Generator(ngram)

    # ユーザのツイートの取得
    twitter = twitter_api.Twitter()
    timeline_texts = twitter.user_timeline_texts(
        screen_name, access_token, access_token_secret)

    # 1件も取得できなかった場合
    if len(timeline_texts) == 0:
        return_json = {
            'error_msg': 'ツイートを取得できませんでした．screen_name が正しいかどうか確認して下さい．'}
        return json.dumps(return_json)  # 1文だけ返す

    # ツイートの前処理
    timeline_texts = twitter.removed_texts(timeline_texts)

    # 文字ngramを生成
    charNgram(gen, timeline_texts)

    # 新たなツイートを生成
    st = START
    for i in xrange(1000):
        voca, prob = ngram.probKN(D, st)
        i = numpy.random.multinomial(1, prob).argmax()
        v = voca[i]
        if v == END:
            break
        st += v

    # screen_name など Tweet の表示に利用する要素の取得
    screen_name, name, profile_image_url_https = twitter.get_user(
        screen_name, access_token, access_token_secret)

    # 現在時刻の取得
    d = datetime.now(pytz.timezone('Asia/Tokyo'))
    time = d.strftime("%Y年%m月%d日 %H:%M")

    # json を生成して返す
    return_json = {'screen_name': screen_name,
                   'name': name,
                   'profile_image_url_https': profile_image_url_https,
                   'time': time,
                   'predicted_tweet': st[1:]}
    return json.dumps(return_json)  # 1文だけ返す
