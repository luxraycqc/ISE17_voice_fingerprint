from features import mfcc
from features import logfbank
import ltsd
import vad
import numpy as np
import pickle
import scipy.io.wavfile as wav
from sklearn.mixture import GMM
import sys
import os

vad_ob = vad.VAD()

def create_account(username):
    """
    generates an account
    """
    write_features(username)
    means, invstds = recalculate_norm()
    return means, invstds, fit_gmm(username, means, invstds)

def fit_gmm(username, means, invstds):
    """
    fit a gmm to the users features
    """
    path = os.path.dirname(os.path.realpath(__file__)) + "/accounts/" + username + "/"
    userfile = username + ".txt"

    # Load userfile, means, and invstds
    try:
        userfeatures = pickle.loads(open(path + userfile, 'r+').read())
    except IOError:
        print "No userfeatures found"

    # Aggregate features
    aggfeatures = None
    for wavpath, features in userfeatures.items():
        normed = normalize(means, invstds, features)
        if aggfeatures is None:
            aggfeatures = normed
        else:
            aggfeatures = np.vstack((aggfeatures, normed))

    gmm = GMM(n_components=10)
    print gmm.fit(aggfeatures)
    return gmm

def write_features(username):
    """ 
    Writes the user's enrollment features to their folder in {their username}.txt
    and adds in the features to allfeatures.txt
    """
    path = os.path.dirname(os.path.realpath(__file__)) + "/accounts/" + username + "/"
    filename = "allfeatures.txt"
    userfile = username + ".txt"

    try:
        allfeatures = pickle.loads(open(filename, 'r+').read())
        os.remove(filename)
    except IOError:
        allfeatures = {}

    userfeatures = {}
    i = 0
    while os.path.isfile(path + str(i) + ".wav"):
        wavpath = path + str(i) + ".wav"
        (rate,sig) = wav.read(wavpath)
        new_sig = filter_sig(rate, sig, path, str(i))
        mfcc_feat = mfcc(new_sig, rate)
        mfcc_feat = np.array(mfcc_feat)
        fbank_feat = logfbank(new_sig, rate)
        if wavpath not in allfeatures:
            allfeatures[wavpath] = mfcc_feat
        userfeatures[wavpath] = mfcc_feat
        i += 1

    pickle.dump(allfeatures, open(filename, 'wb+'))
    pickle.dump(userfeatures, open(path + userfile, 'wb+'))
    return userfeatures, allfeatures

def recalculate_norm():
    """
    Recalculates the invstds and means and returns them
    """
    filename = "allfeatures.txt"
    
    # load all features and recalculate
    try:
        allfeatures = pickle.loads(open(filename, 'r+').read())
    except IOError:
        print "Error, allfeatures.txt does not exist"

    allconcat = np.vstack(list(allfeatures.values()))
    means = np.mean(allconcat, 0) # mean of all features
    invstds = np.std(allconcat, 0) # inverse standard deviations
    
    for i, val in enumerate(invstds):
        if val == 0.0:
            invstds[i] = 1.0
        else:
            invstds[i] = 1.0/val

    return means, invstds


def normalize(means, invstds, features):
    """
    Normalize MFCC features
    """
    return (features - means) * invstds

def filter_sig(fs, signal, path, filename):
    """
    Filter signal
    """
    (fs_noise, signal_noise) = wav.read("noise.wav")
    vad_ob.init_noise(fs_noise, signal_noise)
    ret, intervals = vad_ob.filter(fs, signal)
    orig_len = len(signal)
    wav.write(path + "vaded_" + filename + ".wav", fs, ret)

    if len(ret) > orig_len/3:
        return ret
    return np.array([])

if __name__ == '__main__':
    username = sys.argv[1]
    create_account(username)
    sys.exit(0)