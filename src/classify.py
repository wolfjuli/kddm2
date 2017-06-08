#!/usr/bin/python

from preprocess import preprocess
from parse_emails import *

from time import time
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.externals import joblib

from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier

## CONFIGURATION
# TARGETS (0: Authors, 1: Recipients, 2: Both)
t = 0
# CLASSIFIER (0: Naive Bayes, 1: Decision Tree, 2: SVM, 3: Random Forest, 4: Neural Network, 5: Gradient Boosting)
c = 5

try:
    with open("./data/authors.pkl", "rb") as authors_file, \
            open("./data/word_data.pkl", "rb") as words_file, \
            open("./data/recipients.pkl", "rb") as recipients_file, \
            open("./data/classes.pkl", "rb") as classes:
        authors = pickle.load(authors_file)
        recipients = pickle.load(recipients_file)
        word_data = pickle.load(words_file)
        target_names = np.array(pickle.load(classes))
except Exception as e:
    print("Error in loading prepared data: {}\n Parsing data from database.".format(e))
    word_data, authors, recipients, target_names = parse_mails()

targets = {0: authors, 1: recipients, 2: zip(authors, recipients)}.get(t)
features_train, features_test, labels_train, labels_test = preprocess(word_data, targets)


clfs = {0: ("Naive Bayes", MultinomialNB()),
        1: ("Decision Tree", DecisionTreeClassifier(min_samples_split=10)),
        2: ("SVM", SVC(kernel="rbf", C=10500, verbose=True)),
        3: ("Random Forest", RandomForestClassifier(verbose=3)),
        4: ("Neural Network", MLPClassifier(hidden_layer_sizes=(100,), early_stopping=True, verbose=True)),
        5: ("Gradient Boosting", GradientBoostingClassifier(verbose=1))}
clf = clfs.get(c)[1]
print("\n### CLASSIFICATION using {} ###".format(clfs.get(c)[0]))

t0 = time()
clf.fit(features_train, labels_train)
print("Training time:", round((time()-t0)/60, 2), "m")
joblib.dump(clf, "./data/{} Classifier.pkl".format(clfs.get(c)[0]))

t1 = time()
prediction = clf.predict(features_test)
print("Prediction time:", round((time()-t1)/60, 2), "m")

print(classification_report(labels_test, prediction, target_names=target_names))
print("Accuracy:", accuracy_score(prediction, labels_test))

cnf_matrix = confusion_matrix(labels_test, prediction)
plot_confusion_matrix(cnf_matrix, target_names[np.unique(targets)], normalize=True)
