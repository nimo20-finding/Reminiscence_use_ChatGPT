import base64

import speech_recognition as sr
import streamlit as st
import openai
from PIL import Image
from google.cloud import texttospeech
import pyaudio
import wave
import io
from google.oauth2 import service_account


def tts(text: str, format_name: texttospeech.AudioEncoding) -> bytes:
    credentials = service_account.Credentials.from_service_account_file('secret-key.json')
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        name='ja-JP-Neural2-B',
        language_code="ja-JP",
        ssml_gender=texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=format_name,
        # 読み上げ速度 (0.25～4.0)
        speaking_rate=1,
        # ピッチ (-20.0～20.0)
        pitch=0,
        # ゲイン (-96.0～16.0)。-6で半分。6で2倍。10以下を推奨
        volume_gain_db=0.0,
        # 他にもオプションあり
    )


    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    return response.audio_content


def tts_play(text: str) -> None:
    audio_content = tts(text, texttospeech.AudioEncoding.LINEAR16)
    wav_play(audio_content)


def wav_play(audio_content: bytes) -> None:
    wf = wave.open(io.BytesIO(audio_content), 'rb')

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )

    chunk_size = 1024
    data = wf.readframes(chunk_size)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(chunk_size)

    stream.stop_stream()
    stream.close()

    pa.terminate()

def record():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    output = r.recognize_google(audio, language='ja-JP')
    return output


def main():
    speak = Image.open("speak.png")
    normal = Image.open("normal.png")

    st.set_page_config(
        layout="wide"
    )
    coll, colr = st.columns(2)
    result_area = colr.empty()
    avator_area = coll.empty()

    if "document" not in st.session_state:
        st.session_state.document = [] #ダウンロードファイル用

    if "history_summary" not in st.session_state:
        st.session_state.history_summary = [] #会話の要約用

    if "history_info" not in st.session_state:
        ##################
        # ChatGPTの初期化 #
        ##################
        openai.api_key = ""

        st.session_state.history_info = [] #時事情報ボット用
        gene = "" #10-15際の頃の西暦　例）2009-2014
        first_prompt = f'''あなたは時代別の流行や時事情報を答えてくれるボットです。
                        入力された数字の年代の子どもたちの間で流行していたものや時代背景を答え、以下の###時代情報を更新してください
                        例えば入力された数字が2000-2005だった場合、2000年から2005年の流行や時事情報を答えてください
                        ###時代情報
                        {st.session_state.history_info}'''
        info = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": first_prompt}, {"role": "user", "content": gene}]
        )
        text = "時事情報ボット"
        res = info["choices"][0]["message"]["content"]
        st.session_state.history_info = res
        combined_text = f"{text}: {res}\n"
        st.session_state.document.append(combined_text)


    if "conversationHistory" not in st.session_state:
        st.session_state.conversationHistory = [] #会話内容記録用

        ##################
        # Pyttsx3を初期化 #
        ##################
        system_prompt = f'''私は高齢者で、あなたは介護者です。私たちは回想法として過去の出来事を肯定的に振り返り人生を受容するために会話を行います。
                回想法のテーマは、###時代背景の情報を取り入れて設定してください
                回想法に基づいて私の回答に対して深掘りする質問をしてください
                もし私が質問を聞き返したら、簡単な言葉で言い換えてください
                私が「わからない」「特にない」「思い出したくない」などの回答をしたときは、別の質問に変更してください
                前向きな言葉を使い、共感や、重要なワードの反復を忘れないでください
                過去のつらい経験が受容できるように肯定的な意見でサポートしてください
                時々、私の名前「○○さん」と読んでください。
                また、時々、テーマに沿って今の状況も聞いてください。
                一回の会話で行う質問数は少なくしてください
                基本は敬語で話し、時々親しげに孫のような口調で話してください。

                ###時代背景
                {st.session_state.history_info}'''
        setting = {"role": "system",
                   "content": system_prompt}
        st.session_state.conversationHistory.append(setting)
        question = {"role": "user",
                    "content": "設定に沿ってテーマを一つ定めたら、挨拶をしたあとにその時代に何があったか箇条書きで簡潔に短く伝えて、質問してください"}
        st.session_state.conversationHistory.append(question)
        text = "会話設定"
        combined_text = f"{text}: {question}\n"
        st.session_state.document.append(combined_text)

        avator_area.image(speak, use_column_width=True)

        response = openai.ChatCompletion.create(
            messages=st.session_state.conversationHistory,
            max_tokens=1024,
            n=1,
            stream=True,
            temperature=0.5,
            stop=None,
            presence_penalty=0.5,
            frequency_penalty=0.5,
            model="gpt-3.5-turbo"
        )

        # ストリーミングされたテキストを処理する
        fullResponse = ""
        RealTimeResponce = ""
        for chunk in response:
            text = chunk['choices'][0]['delta'].get('content')

            if (text == None):
                pass
            else:
                fullResponse += text
                RealTimeResponce += text

                result_area.write(
                    ">" + '<span style="font-size:30px;">' + fullResponse.replace('\n', '<br>') + '</span>',
                    unsafe_allow_html=True)

                target_char = ["。", "！", "？", "\n"]
                for index, char in enumerate(RealTimeResponce):
                    if char in target_char:
                        pos = index + 2  # 区切り位置
                        sentence = RealTimeResponce[:pos]  # 1文の区切り
                        RealTimeResponce = RealTimeResponce[pos:]  # 残りの部分
                        # 1文完成ごとにテキストを読み上げる(遅延時間短縮のため)
                        tts_play(sentence)
                        break
                    else:
                        pass

        chatGPT_responce = {"role": "assistant", "content": fullResponse}
        st.session_state.conversationHistory.append(chatGPT_responce)

        text = "ChatGPT"
        combined_text = f"{text}: {chatGPT_responce}\n"
        st.session_state.document.append(combined_text)

    button_style = f'''
                        <style>
                            div.stButton > button:first-child{{
                            background:red;
                            color     :#FFF;
                            font-size : 24px;
                            padding   : 0.5em 1em;}}
                        </style>'''

    st.markdown(button_style, unsafe_allow_html=True)

    show_sidebar = st.checkbox("サイドバーを表示する")
    if show_sidebar:
        if st.sidebar.button("ダウンロード"):
            text_data = '\n'.join(st.session_state.document)
            b64 = base64.b64encode(text_data.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="no1.txt">ダウンロード</a>'
            st.markdown(href, unsafe_allow_html=True)



    if colr.button("音声入力スタート"):
        if len(st.session_state.conversationHistory) < 12:
            avator_area.image(normal, use_column_width=True)

            user_text = record()
            if user_text:
                user_action = {"role": "user", "content": user_text}
                st.session_state.conversationHistory.append(user_action)

                text = "user"
                combined_text = f"{text}: {user_action}\n"
                st.session_state.document.append(combined_text)

                avator_area.image(speak, use_column_width=True)

                response = openai.ChatCompletion.create(
                    messages=st.session_state.conversationHistory,
                    max_tokens=1024,
                    n=1,
                    stream=True,
                    temperature=0.5,
                    stop=None,
                    presence_penalty=0.5,
                    frequency_penalty=0.5,
                    model="gpt-3.5-turbo"
                )

                # ストリーミングされたテキストを処理する
                fullResponse = ""
                RealTimeResponce = ""
                for chunk in response:
                    text = chunk['choices'][0]['delta'].get('content')

                    if (text == None):
                        pass
                    else:
                        fullResponse += text
                        RealTimeResponce += text

                        result_area.write(
                            ">" + '<span style="font-size:30px;">' + fullResponse.replace('\n', '<br>') + '</span>',
                            unsafe_allow_html=True)

                        target_char = ["。", "！", "？", "\n"]
                        for index, char in enumerate(RealTimeResponce):
                            if char in target_char:
                                pos = index + 2  # 区切り位置
                                sentence = RealTimeResponce[:pos]  # 1文の区切り
                                RealTimeResponce = RealTimeResponce[pos:]  # 残りの部分
                                # 1文完成ごとにテキストを読み上げる(遅延時間短縮のため)
                                tts_play(sentence)
                                break
                            else:
                                pass

                # ChatGPTからの応答内容を会話履歴に追加
                chatGPT_responce = {"role": "assistant", "content": fullResponse}
                st.session_state.conversationHistory.append(chatGPT_responce)
                text = "chatGPT"
                combined_text = f"{text}: {chatGPT_responce}\n"
                st.session_state.document.append(combined_text)


        else:
            avator_area.image(normal, use_column_width=True)

            user_text = record()
            user_action = {"role": "user", "content": user_text}
            st.session_state.conversationHistory.append(user_action)
            text = "user"
            combined_text = f"{text}: {user_action}\n"
            st.session_state.document.append(combined_text)

            text_message = ""
            for m in st.session_state.conversationHistory:
                if m["role"] == "user":
                    text_message += "ユーザ：" + m["content"] + "\n"
                if m["role"] == "assistant":
                    text_message += "ChatGPT：" + m["content"] + "\n"
            system_prompt = f'''あなたは会話ログの要約生成・更新マシーンです。
                        入力された会話ログから、簡潔な要約を作成し、以下の###既存の要約情報を更新してください
                        特に固有名詞は必ず含めてください

                        入力される会話ログは以下の形式です。
                        ユーザ：こんにちは
                        ChatGPT：こんにちは。あなたのお名前は何ですか？
                        ユーザ：私は山田太郎です。
                        ChatGPT：山田さん、初めまして。今日は何かお困りごとですか？

                        要約例：
                        ユーザの名前は山田太郎

                        ###既存の要約情報
                        {st.session_state.history_summary}'''

            summary = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text_message}]
            )
            res = summary["choices"][0]["message"]["content"]
            st.session_state.history_summary = res
            text = "会話の要約"
            combined_text = f"{text}: {res}\n"
            st.session_state.document.append(combined_text)

            st.session_state.conversationHistory = []
            system_prompt = f'''私は高齢者で、あなたは介護者です。私たちは回想法として過去の出来事を肯定的に振り返り人生を受容するために会話を行います。
                回想法のテーマは、###時代背景の情報を取り入れて、質問していない（###過去の会話要約情報に含まれない）テーマに設定してください
                回想法に基づいて私の回答に対して深掘りする質問をしてください
                もし私が質問を聞き返したら、簡単な言葉で言い換えてください
                私が「わからない」「特にない」「思い出したくない」などの回答をしたときは、別の質問に変更してください
                前向きな言葉を使い、共感や、重要なワードの反復を忘れないでください
                過去のつらい経験が受容できるように肯定的な意見でサポートしてください
                時々、私の名前「○○さん」と読んでください。
                また、時々、テーマに沿って今の状況も聞いてください。
                一回の会話で行う質問数は少なくしてください
                基本は敬語で話し、時々親しげに孫のような口調で話してください。

                なお、過去の会話要約情報があればその情報も参考にしてください
                ###過去の会話要約情報
                {st.session_state.history_summary}
                ###時代背景
                {st.session_state.history_info}
                '''
            setting = {"role": "system",
                       "content": system_prompt}
            st.session_state.conversationHistory.append(setting)
            question = {"role": "user",
                        "content": "設定に沿って、次の回想法のテーマを決めて質問してください。「たくさんお話ししてくださりありがとうございます。次に、」から始めてください"}
            st.session_state.conversationHistory.append(question)

            avator_area.image(speak, use_column_width=True)

            response = openai.ChatCompletion.create(
                messages=st.session_state.conversationHistory,
                max_tokens=1024,
                n=1,
                stream=True,
                temperature=0.5,
                stop=None,
                presence_penalty=0.5,
                frequency_penalty=0.5,
                model="gpt-3.5-turbo"
            )

            # ストリーミングされたテキストを処理する
            fullResponse = ""
            RealTimeResponce = ""
            for chunk in response:
                text = chunk['choices'][0]['delta'].get('content')

                if (text == None):
                    pass
                else:
                    fullResponse += text
                    RealTimeResponce += text

                    result_area.write(
                        ">" + '<span style="font-size:30px;">' + fullResponse.replace('\n', '<br>') + '</span>',
                        unsafe_allow_html=True)

                    target_char = ["。", "！", "？", "\n"]
                    for index, char in enumerate(RealTimeResponce):
                        if char in target_char:
                            pos = index + 2  # 区切り位置
                            sentence = RealTimeResponce[:pos]  # 1文の区切り
                            RealTimeResponce = RealTimeResponce[pos:]  # 残りの部分
                            # 1文完成ごとにテキストを読み上げる(遅延時間短縮のため)
                            tts_play(sentence)
                            break
                        else:
                            pass

            # ChatGPTからの応答内容を会話履歴に追加
            chatGPT_responce = {"role": "assistant", "content": fullResponse}
            st.session_state.conversationHistory.append(chatGPT_responce)
            text = "chatGPT"
            combined_text = f"{text}: {chatGPT_responce}\n"
            st.session_state.document.append(combined_text)


    else:
        tts_play("赤いボタンを押してから話してください")
        avator_area.image(normal, use_column_width=True)


if __name__ == '__main__':
    main()