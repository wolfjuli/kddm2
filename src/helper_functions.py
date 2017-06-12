# !/usr/bin/env python2.7

import os
import sys
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from nltk.stem.snowball import SnowballStemmer


def getListOfFiles(root):

    ret = []
    for path, subdirs, files in os.walk(root):
        #print path

        for file in [f for f in files if not f.startswith(".")]:
            ret += [os.path.join(path, file)]

        for subdir in subdirs:
            #print "calling for " + os.path.join(path, subdir)
            ret += getListOfFiles(os.path.join(path, subdir))

    return ret


def getParsedContent(filefullpath):
    ret = {}

    with open(filefullpath, 'rb') as f:
        mailcontent = f.read().decode('utf8', 'ignore')

    lines = mailcontent.replace("\r", "").split("\n")
    isBody = 0
    mailBody = ""
    lastKey = ""
    # print "mail has " + str(len(lines)) + " lines"
    for line in lines:
        if isBody == 1:
            mailBody += line + "\n"
            continue
        elif line == "":
            isBody = 1
            continue

        parts = line.split(": ")

        if len(parts) < 2 or line.startswith('	') or line.startswith(' '):
            #print "corrupt line in header in '" + filefullpath + "', last key: " + lastKey + ", line: " + line
            key = lastKey
            if lastKey == "":
                print("This file has a corrupt header: {}".format(filefullpath))
            ret[lastKey] += "\n" + ": ".join(parts)
            #print "value now: " + ret[lastKey]
        else:
            key = parts[0]
            del parts[0]
            ret[key] = ": ".join(parts)

        lastKey = key

    ret['body'] = mailBody
    ret['SHABody'] = str(hashlib.sha256(mailBody.encode('UTF-8')).hexdigest())
    ret['filepath'] = filefullpath

    return ret


def strip(text, chars):
    for c in chars:
        text = text.replace(c, "")
    return text


def stem(row):
    stemmer = SnowballStemmer("english")
    names = row[0].lower().split("@")[0].split(".") + row[1].lower().split("@")[0].split(".")
    text = strip(row[2].lower(), names)
    words = [stemmer.stem(word) for word in text.split()]
    return " ".join(words)


def plot_confusion_matrix(cm, targets, name, normalize=True, show=True):
    if normalize:
        title = "Normalized confusion matrix of {}".format(name)
        np.set_printoptions(precision=2)
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    else:
        title = "Confusion matrix of {}".format(name)

    plt.figure(figsize=(13, 13))
    plt.imshow(cm, interpolation='none')
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(targets))
    plt.xticks(tick_marks, targets, rotation=90, fontsize=int(500/len(targets)))
    plt.yticks(tick_marks, targets, fontsize=int(500/len(targets)))
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig("../results/{} CM.png".format(name))
    if show:
        plt.show()


class Logger(object):
    def __init__(self, name):
        if isinstance(sys.stdout, Logger):
            sys.stdout.log.close()
            self.terminal = sys.stdout.terminal
        else:
            self.terminal = sys.stdout

        self.log = open("../results/{}.log".format(name), "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.log.close()
        pass