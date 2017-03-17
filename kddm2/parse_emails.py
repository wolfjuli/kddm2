#!/usr/bin/python

from nltk.stem.snowball import SnowballStemmer
import string
import os
import pickle


def parseEmail(f):
    f.seek(0)
    all_text = f.read()

    content = all_text.split("X-FileName:")
    words = ""
    if len(content) > 1:
        text_string = content[1].translate(string.maketrans("", ""), string.punctuation)
        stemmer = SnowballStemmer("english")

        words = []
        for word in text_string.split():
            words.append(stemmer.stem(word))

    return string.join(words)


def removeNames(text, names):
    for name in names:
        text = text.replace(name, "")
    return text


def countLines(file):
    c = sum(1 for _ in file)
    file.seek(0)
    return c

def parseEmails():
    authors = []
    emails = []
    cnt = 0
    progress = 0

    print "\n### PARSING EMAILS ###"
    with open("from_sara.txt", "r") as from_sara, open("from_chris.txt", "r") as from_chris:
        filecount = countLines(from_sara) + countLines(from_chris)
        for name, from_person in [("sara", from_sara), ("chris", from_chris)]:
            for path in from_person:
                cnt += 1
                try:
                    with open(os.path.join('..', path[:-1]), "r") as email:
                        words = removeNames(parseEmail(email), ["sara", "shackleton", "chris", "germani"])
                        emails.append(words)
                        authors.append(0 if name == "sara" else 1)
                except:
                    print "error parsing email " + path

                tmp_progress = int(cnt*100 / filecount)
                if (tmp_progress % 10 == 0 and progress != tmp_progress):
                    progress = tmp_progress
                    print "-- {} / {} emails parsed ({} %)".format(cnt, filecount, progress)

    print "-- {} emails parsed".format(cnt)

    return emails, authors


if __name__ == "__main__":
    emails, authors = parseEmails()
    pickle.dump(emails, open("word_data.pkl", "w"))
    pickle.dump(authors, open("authors.pkl", "w"))
