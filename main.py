import os
import subprocess
import json
import openai
import time
import pyaudio
import wave
import audioop
from dotenv import load_dotenv


def voice_rec():
    po = pyaudio.PyAudio()

    for index in range(po.get_device_count()):
        desc = po.get_device_info_by_index(index)
        # if desc["name"] == "record":
        print("DEVICE: %s  INDEX:  %s  RATE:  %s " % (desc["name"], index, int(desc["defaultSampleRate"])))

    FORMAT = pyaudio.paInt16
    CHANNELS = 16
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 10
    WAVE_OUTPUT_FILENAME = "./sound/question.wav"

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    sound_volume = 500

    os.system("mpg123 ./sound/rec.mp3")
    print("---음성 녹음 시작---")

    while True:
        data = stream.read(CHUNK)
        rms = audioop.rms(data, 2)
        if rms > sound_volume:
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            break

    print("---음성 녹음 완료---")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    time.sleep(0.1)


def chat_gpt_speak():
    load_dotenv()
    openai.organization = "org-oMb8n1ArLu6XkrsXxXNg9hQQ"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.Model.list()

    for cmd in [""" curl https://api.openai.com/v1/audio/transcriptions \
                  -H "Authorization: Bearer $OPENAI_API_KEY" \
                  -H "Content-Type: multipart/form-data" \
                  -F file="@./sound/question.wav" \
                  -F model="whisper-1" """]:

        words = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        json_list = json.loads(words)

        speech_text = json_list["text"]

        print(json_list["text"])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": speech_text},
        ],
    )

    answer = response.choices[0]["message"]["content"].strip()
    print(answer)
    time.sleep(0.5)

    voice = """ curl -v \
                  -H "x-api-key: 91ce013c97b577b8f4c8d354e675b883" \
                  -H "Content-Type: application/xml" \
                  -H "X-TTS-Engine: deep" \
                  -d '<speak>
                      <voice name="Nora">{0}</voice>
                      </speak>' \
                  https://94a32363-bfe6-4c43-8cd5-0ecb45a376e6.api.kr-central-1.kakaoi.io/ai/text-to-speech/d7504f19ae0e4390b7c790dc2e2d4226 > ./sound/answer.mp3 && mpg123 ./sound/answer.mp3 """.format(answer)
    os.system(voice)
    time.sleep(10)


if __name__ == "__main__":
    os.system("mpg123 ./sound/start.mp3")
    time.sleep(2)

    while True:
        voice_rec()
        chat_gpt_speak()
