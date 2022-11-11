import azure.cognitiveservices.speech as speechsdk
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()

SUBSCRIPTION_KEY = os.environ.get('AZURE_SPEECH_SUBSCRIPTION_KEY')
REGION = 'japaneast'
file_name = 'tukaremaru-avatar'
done = False
output = []


def from_file():
    speech_config = speechsdk.SpeechConfig(subscription=SUBSCRIPTION_KEY, region=REGION, speech_recognition_language='ja-JP')
    audio_input = speechsdk.AudioConfig(filename="{}.wav".format(file_name))

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: output_called(evt))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()


def output_called(evt):
    print('{}'.format(evt.result.text))
    result = {
        "offset": evt.result.offset,
        "duration": evt.result.duration,
        "text": evt.result.text
    }
    # output.append(evt.result.text + "\n")
    output.append(result)


def stop_cb(evt):
    """callback that signals to stop continuous recognition upon receiving an event `evt`"""
    print('CLOSING on {}'.format(evt))
    global done
    done = True


from_file()

with open("transcription_{}.json".format(file_name), "w") as f:
    json.dump(output, f, ensure_ascii=False)
