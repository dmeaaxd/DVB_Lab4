import json
import pyttsx3
import pyaudio
import requests
import vosk

tts = pyttsx3.init()
voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    # print(voice.name)
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        tts.setProperty('voice', voice.id)

model = vosk.Model('vosk-model-small-ru-0.4')
record = vosk.KaldiRecognizer(model, 16000)

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 frames_per_buffer=8000)
stream.start_stream()


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def speak(say):
    tts.say(say)
    tts.runAndWait()


class Weather:
    def init(self):
        self.weather_data = None
        self.temperature = None
        self.wind_speed = None
        self.wind_direction = None

    def get(self):
        url = 'https://wttr.in/Saint-Petersburg?format=%C\n%t\n%w\n'
        data = requests.get(url).text.split('\n')
        self.weather_data = data
        self.temperature = int(data[1].replace('°C',''))
        self.wind_speed = int(data[2][1:].replace('km/h',''))
        self.wind_direction = data[2][0]

    def is_good_for_walk(self):
        if self.temperature < 5 or self.wind_speed > 15:
            return False
        return True


weather = None


def parse(text):
    global weather

    if text not in ['погода', 'ветер', 'направление', 'записать', 'прогулка', 'выход']:
        print('unrecognized command:', text)
        return

    if text == 'погода':
        if not weather:
            weather = Weather()
            weather.get()
        print(f'Temperature: {weather.temperature} °C')
        print(f'Wind speed: {weather.wind_speed} Km/h')
        print(f'Wind direction: {weather.wind_direction}')
    elif text == 'ветер':
        if not weather:
            weather = Weather()
            weather.get()
        print(f'Wind speed: {weather.wind_speed} Km/h')
    elif text == 'направление':
        if not weather:
            weather = Weather()
            weather.get()
        print(f'Wind direction: {weather.wind_direction}')
    elif text == 'записать':
        if not weather:
            weather = Weather()
            weather.get()
        with open('weather.txt','w',encoding="utf-8") as f:
            f.write(f'{weather.temperature}°C, {weather.wind_direction}{weather.wind_speed} Km/h')
            print('saved')
    elif text == 'прогулка':
        if not weather:
            weather = Weather()
            weather.get()
        if weather.is_good_for_walk():
            print('Good for a walk!')
        else:
            print('Not recommended for a walk')
    elif text == 'выход':
        quit()


print('start')
for text in listen():
    parse(text)