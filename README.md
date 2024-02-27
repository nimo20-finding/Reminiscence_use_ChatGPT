# 私の実装環境

* OS: Windows
* IDE: PyCharm（2023.3.2）

## Python・ライブラリのバージョン一覧

| ライブラリ等 | バージョン |
| --- | --- |
| Python | 3.9.0 |
| SpeechRecognition | 3.8.1 |
| streamlit | 1.30.0 |
| openai | 0.28.0 |
| PyAudio | 0.2.14 |
| google-cloud-texttospeech | 2.16.2 |

---

# 動かせるようになるまで
## PythonとPyCharmをインストールする
* [Pythonのダウンロードページ](https://www.python.org/downloads/)からPythonをダウンロードして、インストールしてください。

* PyCharmのダウンロード・インストールは[こちらのサイト](https://sukkiri.jp/technologies/ides/pycharm/pycharm-win.html)などを参考にしてください。


## APIの使用のためにアカウントを作成する
* 本プロジェクトではChatGPT APIおよびGoogle Cloud Text-to-Speech APIを使用するため、OpenAIおよびGoogle Cloud Platformのアカウントを作成してください。

* OpenAIのアカウント作成およびChatGPT APIの使い方は[ChatGPT API利用方法の簡単解説](https://qiita.com/mikito/items/b69f38c54b362c20e9e6)、Google Cloud Platformの利用登録は[Google Cloud Text-to-Speechの使い方　日本語テキストを読み上げさせてみよう](https://blog.apar.jp/web/9893/)が参考になります。


| | OpenAI | Google Cloud Platform |
| --- | --- | --- |
| アカウント作成時に必要な情報 | メールアドレス、パスワード、氏名、生年月日、電話番号*1 | Googleアカウント、住所、名前、電話番号、クレジットカード番号 |
| 無料期間 | 最初の3か月間は$18まで無料*2 | 無料トライアルや無料枠あり*3 |
| 課金制度 | 従量課金制、月単位で請求、1000トークンあたり$0.002 | 従量課金制、月単位で請求 |

*1 GoogleアカウントやMicrosoftアカウントでもアカウントを作成できる。

*2 OpenAIアカウントを作成してから3か月間のため、ChatGPTをブラウザで使用したことのある人は期限に注意。期限や$18の使用上限を超えると、クレジットカードと紐づけた有料枠へのアップグレードが必要となる。

*3 このプログラムで使用するGoogle Cloud Text-to-Speechでは課金を有効にする必要があるが、月100万文字までは無料で使用可能


* OpenAIのAPI Keyを控えてください。

* Google Cloud Platformで作成したキーファイル（JSONファイル）をダウンロードし、secret-key.jsonに名前を変更してください。


## 必要なファイルを用意する
* このプロジェクトのクローンをZIPファイルでダウンロードし、解凍してください。

* PyCharmにて適当な新しいプロジェクトを作成し、先ほど解凍して取得した3つのファイルおよびGoogle Cloud Platformのキーファイル（secret-key.json）を同一階層に置いてください。


## 適宜コードを書き換える
以下の部分を、適宜書き換えてください

| 行数 | 書き換える場所 |
| --- | --- |
| 97 | openai.api_keyにOpenAI API Keyを指定 |
| 100 | geneにユーザが10-15歳の頃の西暦を指定 |
| 130 | 「○○さん」の○○にはユーザのあだ名を指定 |
| 330 | 同上 |
| 212 | download="no1.text"はユーザごとにnoの後の数字を変更すると良い |


## 実行する
PyCharmのTerminalにてstreamlit run main.pyを実行するとブラウザにてstreamlitが立ち上がり動作を確認できると思います。
