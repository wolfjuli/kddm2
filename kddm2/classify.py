#!/usr/bin/python

import pickle
import cPickle

from time import time
from preprocess import preprocess
from parse_emails import parseEmails
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

try:
    with open("authors.pkl", "r") as authors_file, open("word_data.pkl", "r") as words_file:
        authors = pickle.load(authors_file)
        word_data = cPickle.load(words_file)
    features_train, features_test, labels_train, labels_test = preprocess(word_data, authors)
except:
    features_train, features_test, labels_train, labels_test = preprocess(*parseEmails())

print "\n### CLASSIFICATION ###"
clf = MultinomialNB()
#clf = DecisionTreeClassifier(min_samples_split=40)
#clf = SVC(kernel="rbf", C=10500)

t0 = time()
clf.fit(features_train, labels_train)
print "Training time:", round(time()-t0, 3), "s"

t1 = time()
prediction = clf.predict(features_test)
print "Prediction time:", round(time()-t1, 3), "s"
print accuracy_score(prediction, labels_test)

chris = []
for i in prediction:
    if i == 1:
        chris.append(i)

print len(chris)
