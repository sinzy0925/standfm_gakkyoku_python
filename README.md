# standfm_gakkyoku_python
プログラミング言語：python 

ライブラリ：playwright

詳細設計書：https://chatgpt.com/share/66f5f525-962c-8002-a1a9-2c448e09f18b

アプリを作った理由と、デモ：https://www.instagram.com/reel/DAYDnD2unXa/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==

概要：

・音声配信SNSのstand.fmでは、歌を歌うと楽曲申請が必要です。

・楽曲申請の方法：

A)　JASRACかNexToneでその歌の、

  ①作品コード②作品タイトル③アーティスト名④作詞者⑤作曲者を調べる。

B)　stand.fmの楽曲申請画面に入力する

・上記A)b）を自動化したのが、このアプリです。

・起動方法　１曲の場合（１行で全て記述）

>python standfm_gakkyoku.py メルアド^パスワード^"作品コード,アーカイブの順番"

・起動方法　２曲の場合（１行で全て記述）

>python standfm_gakkyoku.py メルアド^パスワード^"作品コード,アーカイブの順番"^"作品コード,アーカイブの順番"

