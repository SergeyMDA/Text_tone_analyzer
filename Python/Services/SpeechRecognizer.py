# Copyright © 2017-2018. All rights reserved.
# Authors: German Yakimov, Aleksey Sheboltasov
# License: https://github.com/GermanYakimov/Text_tone_analyzer/blob/master/LICENSE
# Contacts: german@yakimov.su, alekseysheboltasov@gmail.com

import speech_recognition as sr
import logging


# Create class
def check_microphone():
    try:
        with sr.Microphone() as source:
            pass
        return True
    except sr.RequestError:
        return False


def recognize_speech():
    r = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                audio = r.listen(source)
        except sr.RequestError:
            return 'No microphone'

        try:
            string = r.recognize_google(audio, language="ru-RU").lower().strip()
            logging.info('\nrecognised speech: %s\n' % string)
            return string

        except sr.UnknownValueError as e:
            logging.error('\n{0}\n'.format(e))
            return 'Unknown value'

        except sr.RequestError as e:
            logging.error('\nspeech recognition: {0}\n'.format(e))
            return 'Internet connection lost'

        except sr.WaitTimeoutError as e:
            logging.error('\n{0}\n'.format(e))
            return None
