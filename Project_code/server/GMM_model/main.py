#!/usr/bin/env python -W ignore::DeprecationWarning
import account as ac
import create_account as ca
import write_audio as wa
import scipy.io.wavfile as wav
import sys
from features import mfcc
import numpy as np
import pickle
import os
import ltsd
import vad
import verify as verify

accounts = {}
means = None
invstds = None
def normalize(means, invstds, data):
    return (data - means) * invstds

def filter_sig(fs, signal):
    vad_ob = vad.VAD()
    (fs_noise, signal_noise) = wav.read("noise.wav")
    vad_ob.init_noise(fs_noise, signal_noise)
    ret, intervals = vad_ob.filter(fs, signal)
    orig_len = len(signal)

    # if len(ret) > orig_len/3:
    #     wavfile.write('vaded.wav', fs, ret)
    #     return ret
    # return np.array([])
    wav.write('vaded.wav', fs, ret)
    return ret

def main():
    global accounts
    global means
    global invstds
    if means == None and os.path.isfile("allfeatures.txt"):
        means, invstds = ca.recalculate_norm()
    try:
        accounts = pickle.loads(open("accounts.txt", 'r+').read())
        os.remove("accounts.txt")
    except IOError:
        pass
    while True:
        call = raw_input("Do you want to login (l) or create a new account (c)? \n")
        if call == "l":
            """
            User decides to log in
            """
            username = raw_input("username: ")
            wa.record_noise()
            wa.write_temp_audio(username)

            wavpath = "temp.wav"
            (rate,sig) = wav.read(wavpath)
            new_sig = filter_sig(rate, sig)
            mfcc_feat = mfcc(new_sig, rate)
            mfcc_feat = np.array(mfcc_feat)

            best_label = ""
            best_ll = -9e99

            for label, account in accounts.items():
                features = normalize(means, invstds, mfcc_feat)
                ll = account.gmm.score_samples(features)[0]
                ll = np.sum(ll)
                print label, ll
                if ll > best_ll:
                    best_ll = ll
                    best_label = label
            print best_ll
            print best_label
            if username != best_label:
                print "I do not think that account belongs to you"
            else:
                print "Yay! You are now logged in"

        elif call == "c":
            """
            User decides to create a new account
            """
            username = raw_input("Please select a username \n")
            path = os.path.dirname(os.path.realpath(__file__)) + "/accounts/" + username + "/"
            if os.path.exists(path):
                print "Please select another username"
                continue
            verify.generate_key(username)
            wa.record_noise()
            for x in range(3):
                wa.write_audio(username)
            print "Done recording! Creating account now"
            accounts[username] = ac.Account(username)
            means, invstds = accounts[username].create_account()
            for account in accounts:
                if account != username:
                    accounts[account].fit_gmm(means, invstds)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Interrupted'
        pickle.dump(accounts, open("accounts.txt", 'wb+'))
        sys.exit(0)
    except Exception as e:
        print e
        print 'Problem with Speech Recognition -- please run in debug mode'
        pickle.dump(accounts, open("accounts.txt", 'wb+'))
        sys.exit(0)