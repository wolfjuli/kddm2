#!/usr/bin/python

import pickle
import cPickle

from time import time
from preprocess import preprocess
from parse_emails import parseEmails
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

try:
    with open("./data/authors.pkl", "r") as authors_file, open("./data/word_data.pkl", "r") as words_file:
        authors = pickle.load(authors_file)
        word_data = cPickle.load(words_file)
    features_train, features_test, labels_train, labels_test = preprocess(word_data, authors)
except:
    features_train, features_test, labels_train, labels_test = preprocess(*parseEmails())


print("\n### CLASSIFICATION ###")

#NB, DT, SVM, (HSVM?) ANN, KNN, RF,
clf = MultinomialNB()
#clf = DecisionTreeClassifier(min_samples_split=40)
#clf = SVC(kernel="rbf", C=10500)

t0 = time()
clf.fit(features_train, labels_train)
print("Training time:", round(time()-t0, 3), "s")

t1 = time()
prediction = clf.predict(features_test)
print("Prediction time:", round(time()-t1, 3), "s\n")

print(classification_report(labels_test, prediction, target_names=["sara", "chris"]))
print("Accuracy:", accuracy_score(prediction, labels_test))
print("Confusion Matrix: \n" , confusion_matrix(labels_test, prediction))
