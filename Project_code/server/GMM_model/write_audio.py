import speech_recognition as sr
import sys
import os
import pyaudio
import wave
#import random_word_generator as rand
from random_words import RandomWords
import random 
from fuzzywuzzy import fuzz
import verify as verify

#rw = rand.Random_Generator()
def check_words(goog_str, words):
    words_string = " ".join(words)
    goog_str = goog_str.lower()
    print words_string, goog_str
    ratio = fuzz.ratio(goog_str, words_string)
    print ratio
    if ratio >=80:
        return True
    return False

def write_temp_audio(username):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r = sr.Recognizer()
        rw = RandomWords()
        while True:
            r.adjust_for_ambient_noise(source)
            count = random.randint(8,10)
            words = rw.random_words(count = count)
            print "Please say the following words:"
            print " ".join(words)
            audio = r.listen(source, timeout = 10)
            signal = audio.get_wav_data()

            # Server sends encrypted symmetric key. Note in this case, the username in this prototype is a way to associate
            # a private/public key pair with a client. These are not associated with the user
            verify.register_keyfile(username)
            serverkey, key = verify.generate_symmetric_key(verify.get_public_key(username))

            # Client decrypts symmetric key
            key = verify.rsa_decrypt(verify.get_private_key(username), key)
            
            # Encrypt with symmetric key
            encrypted = verify.encrypt_sym(key, signal)
            signature = verify.sign_wav(signal, username)

            # Mimicking sending signature and encrypted audio to server.
            # Now server decrypts the bytes and verifies
            new_signal = verify.decrypt_sym(serverkey, encrypted)
            verified = verify.verify_wav(new_signal, username, signature)

            check = check_words(str(r.recognize_google(audio)), words)
            if check:
                break
            else:
                print "Your words did not match. Please repeat the words."
                print words
                continue

    with open("temp.wav", "wb") as f:
        f.write(new_signal)

def record_noise():
    """
    Records noise to use in LTSD algorithm
    """
    print "Please stay silent as we record the background noise of your current surroundings."
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "noise.wav"

    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16, channels = 2, rate = 44100,
        input = True, frames_per_buffer=1024)
    print "Recording background noise..."
    frames = []
    for i in range(0, int(44100 /1024*5)):
        data = stream.read(1024)
        frames.append(data)
    print "Finished recording background noise."

    stream.stop_stream()
    stream.close()
    p.terminate()

    waveFile = wave.open("noise.wav", 'wb')
    waveFile.setnchannels(2)
    waveFile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    waveFile.setframerate(44100)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    return

def write_audio(username):
    """
    Obtains audio from the microphone and writes a .wav if the spoken phrase matches the passphrase
    """
    r = sr.Recognizer()
    rw = RandomWords()
    count = random.randint(8,10)
    words = rw.random_words(count = count)
    while True:
        passed = False
        with sr.Microphone() as source:
            while True:
                r.adjust_for_ambient_noise(source)
                words = rw.random_words(count = count)
                print "Please read the following words"
                print " ".join(words)
                audio = r.listen(source, timeout=10)
                signal = audio.get_wav_data()
                print "Processing..."
                # Mimicking sending it to server. Send audio and bytes of audio
                signature = verify.sign_wav(signal, username)

                # Verify the wav
                verified = verify.verify_wav(signal, username, signature)
                # if not verified, it will raise an InvalidSignatureError

                # Is verified, can go on to complete writing the audio to the server
                goog_str = str(r.recognize_google(audio))
                check = check_words(goog_str, words)
                if check:
                    print "Recognized String"
                    if not os.path.exists("accounts/" + username):
                        os.makedirs("accounts/" + username)
                    path = os.path.dirname(os.path.realpath(__file__)) + "/accounts/" + username + "/"
                    i = 0
                    while os.path.isfile(path + str(i) + ".wav"):
                        i += 1
                    filename = path + str(i) + ".wav"
                    print filename
                    with open(filename, "wb") as f:
                        f.write(audio.get_wav_data())
                    break
                else:
                    with open('badaudio', "wb") as f:
                        f.write(audio.get_wav_data())
                    print "Google thinks you said " + r.recognize_google(audio) + ". Your words did not match."
                    continue
            
        break

if __name__ == '__main__':
    username = sys.argv[1]
    write_audio(username)
    print "Done Recording!"
    sys.exit(0)