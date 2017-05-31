#!/usr/bin/python

import pickle
import matplotlib.pyplot as plt
import itertools
import numpy as np

from time import time
from preprocess import preprocess
from parse_emails import *
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

## CONFIGURATION
# TARGETS (0: Authors, 1: Recipients, 2: Both)
t = 0
# CLASSIFIER (0: Naive Bayes, 1: Decision Tree, 2: SVM)
#NB, DT, SVM, (HSVM?) ANN, KNN, RF,
c = 0

def plot_confusion_matrix(cm, classes, normalize=True, title='Confusion matrix'):
    np.set_printoptions(precision=2)
    plt.figure()
    plt.imshow(cm, interpolation='nearest')
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize: cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    print(cm)
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j], horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()

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
    word_data, authors, recipients, target_names = parseEmailsFromDB()

targets = {0: authors, 1: recipients, 2: zip(authors, recipients)}
features_train, features_test, labels_train, labels_test = preprocess(word_data, targets.get(t))

print("\n### CLASSIFICATION ###")
clfs = {0: MultinomialNB(),
        1: DecisionTreeClassifier(min_samples_split=40),
        2: SVC(kernel="rbf", C=10500)}
clf = clfs.get(c)

t0 = time()
clf.fit(features_train, labels_train)
print("Training time:", round(time()-t0, 3), "s")

t1 = time()
prediction = clf.predict(features_test)
print("Prediction time:", round(time()-t1, 3), "s\n")

print(classification_report(labels_test, prediction, target_names=target_names))
print("Accuracy:", accuracy_score(prediction, labels_test))

print("Confusion Matrix: \n")
cnf_matrix = confusion_matrix(labels_test, prediction)
#plot_confusion_matrix(cnf_matrix, classes=target_names, normalize=True, title='Normalized confusion matrix')