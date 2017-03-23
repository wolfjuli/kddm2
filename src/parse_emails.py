#!/usr/bin/python

from nltk.stem.snowball import SnowballStemmer
from string import maketrans, punctuation, digits, join
import os
import pickle


def parseEmail(path):
    with open(os.path.join('..', path[:-1]), "r") as email:
        email.seek(0)
        all_text = email.read()

        content = all_text.split("X-FileName:")
        if len(content) > 1:
            text_string = content[1].translate(maketrans("", ""), punctuation + digits)
            text_string = removeNames(text_string.lower(), ["sara", "shackleton", "chris", "germany",
                                                            "sshacklensf", "cgermannsf","sshackl", "cgermane"])
            text_string = text_string.lower()
            stemmer = SnowballStemmer("english")
            words = [stemmer.stem(word) for word in text_string.split()]
            return join(words)
        else:
            return ""


def removeNames(text, names):
    for name in names:
        text = text.replace(name, "")
    return text


def countLines(file):
    c = sum(1 for _ in file)
    file.seek(0)
    return c

def parseEmails():
    authors, emails, cnt, progress = [], [], 0, 0

    print "\n### PARSING EMAILS ###"
    with open("./data/from_sara.txt", "r") as from_sara, open("./data/from_chris.txt", "r") as from_chris:
        filecount = countLines(from_sara) + countLines(from_chris)
        for i, from_person in [(0, from_sara), (1, from_chris)]:
            for path in from_person:
                cnt += 1
                try:
                    emails.append(parseEmail(path))
                    authors.append(i)
                except:
                    print "error parsing email " + path

                tmp_progress = int(cnt*100 / filecount)
                if (tmp_progress % 10 == 0 and progress != tmp_progress):
                    progress = tmp_progress
                    print "-- {} / {} emails parsed ({} %)".format(cnt, filecount, progress)

    print "-- {} emails parsed".format(cnt)
    pickle.dump(emails, open("./data/word_data.pkl", "w"))
    pickle.dump(authors, open("./data/authors.pkl", "w"))
    return emails, authors


if __name__ == "__main__":
    parseEmails()