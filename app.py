#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tweet Predictor の本体．
"""
import os
import sys
import logging
from flask import Flask, redirect, request, render_template
from flask_sslify import SSLify
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/py')
import twitter_api
import knlm

logging.warn('app start!')
app = Flask(__name__)
if 'DEV_ENV' not in os.environ:
    sslify = SSLify(app)  # 本番環境では http -> https へリダイレクト

# set the secret key.  keep this really secret:
app.secret_key = os.environ['SECRET_KEY']


@app.route('/')
def index():
    """ root ページの表示 """
    # 必要情報を Twitter API から取得
    twitter = twitter_api.Twitter()
    access_token, access_token_secret, screen_name = twitter.get_access_token()
    redirect_url = twitter.get_authorization_url()

    # レンダリング
    return render_template('index.html', redirect_url=redirect_url,
                           access_token=access_token,
                           access_token_secret=access_token_secret,
                           screen_name=screen_name)


@app.route('/predict', methods=['GET'])
def predict():
    """ Tweet を予測した結果を json で返す API """
    # ajax かつ ROOT_URL からのアクセスのみ許可
    if 'HTTP_REFERER' in request.environ:
        if request.environ['HTTP_REFERER'].startswith(os.environ['ROOT_URL']) == False:
            return 'Error: 外部からのアクセスは禁止されています．'
    else:
        return 'Error: 外部からのアクセスは禁止されています．'
    if request.is_xhr == False:
        return 'Error: Ajaxによる通信のみ許可されています．'

    # 引数取得
    screen_name = request.args.get('screen_name')
    n = request.args.get('n')
    access_token = request.args.get('access_token')
    access_token_secret = request.args.get('access_token_secret')

    # json で結果を返す
    predicted_tweet = knlm.predict(
        screen_name, n, access_token, access_token_secret)
    return predicted_tweet
