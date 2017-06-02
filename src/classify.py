#!/usr/bin/python

import numpy as np
from time import time
from preprocess import preprocess
from parse_emails import *
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.externals import joblib

from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier


## CONFIGURATION
# TARGETS (0: Authors, 1: Recipients, 2: Both)
t = 0
# CLASSIFIER (0: Naive Bayes, 1: Decision Tree, 2: SVM, 3: KNN, 4: Random Forest, 5: Neural Network)
c = 3

try:
    with open("./data/authors.pkl", "rb") as authors_file, \
            open("./data/word_data.pkl", "rb") as words_file, \
            open("./data/recipients.pkl", "rb") as recipients_file, \
            open("./data/classes.pkl", "rb") as classes:
        authors = pickle.load(authors_file)
        recipients = pickle.load(recipients_file)
        word_data = pickle.load(words_file)
        target_names = pickle.load(classes)
except Exception as e:
    print("Error in loading prepared data: {}\n Parsing data from database.".format(e))
    word_data, authors, recipients, target_names = parse_mails()

targets = {0: authors, 1: recipients, 2: zip(authors, recipients)}
features_train, features_test, labels_train, labels_test = preprocess(word_data, targets.get(t))


clfs = {0: ("Naive Bayes", MultinomialNB()),
        1: ("Decision Tree", DecisionTreeClassifier(min_samples_split=40)),
        2: ("SVM", SVC(kernel="rbf", C=10500)),
        3: ("Nearest Neighbors", KNeighborsClassifier(len(np.unique(targets.get(t))))),
        4: ("Random Forest", RandomForestClassifier()),
        5: ("Neural Network", MLPClassifier(early_stopping=True))}
clf = clfs.get(c)[1]
print("\n### CLASSIFICATION using {} ###".format(clfs.get(c)[0]))

t0 = time()
clf.fit(features_train, labels_train)
print("Training time:", round((time()-t0)/60, 2), "m")
joblib.dump(clf, "./data/{} Classifier.pkl".format(clfs.get(c)[0]))

t1 = time()
prediction = clf.predict(features_test)
print("Prediction time:", round((time()-t0)/60, 2), "m")

print(classification_report(labels_test, prediction, target_names=target_names))
print("Accuracy:", accuracy_score(prediction, labels_test))

print("Confusion Matrix: \n")
cnf_matrix = confusion_matrix(labels_test, prediction)
print(cnf_matrix)
