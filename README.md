# Tweet Predictor
指定したユーザが呟きそうなツイートを自動生成するWebサービスです．  
下記URL (heroku上) で実際に稼働しています．  
https://tweet-predictor.herokuapp.com/

## 環境変数について
このアプリを稼働させるには以下の環境変数をセットする必要があります．

```
CONSUMER_KEY    # Twitter API へのアクセスに必要
CONSUMER_SECRET # Twitter API へのアクセスに必要
SECRET_KEY      # 任意の半角英数字 (例: ehdN!bknk/eD.cDECG)
ROOT_URL        # アプリのURL (例: https://tweet-predictor.herokuapp.com/)
DEV_ENV=True    # 開発環境であることを示す．本番環境では不要．
```

## スペシャルサンクス
言語モデルの生成には以下を参考にさせて頂きました．  
https://github.com/shuyo/iir/blob/master/ngram/knlm.py