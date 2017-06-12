#!/usr/bin/python

from preprocess import preprocess
from parse_emails import *
from helper_functions import Logger

from time import time
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.externals import joblib

from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier

try:
    with open("./data/authors.pkl", "rb") as authors_file, \
            open("./data/word_data.pkl", "rb") as words_file, \
            open("./data/recipients.pkl", "rb") as recipients_file, \
            open("./data/classes.pkl", "rb") as classes_file:
        authors = pickle.load(authors_file)
        recipients = pickle.load(recipients_file)
        word_data = pickle.load(words_file)
        classes = np.array(pickle.load(classes_file))
except Exception as e:
    print("Error in loading prepared data: {}\n Parsing data from database.".format(e))
    word_data, authors, recipients, classes = parse_mails()


## CONFIGURATION
t = 1
c = 3

target_options = {0: ("Authors", authors),
                  1: ("Recipients", recipients),
                  2: ("AuthorsAndRecipients)", zip(authors, recipients))}

clfs = {0: ("Naive Bayes", MultinomialNB()),
        1: ("Decision Tree", DecisionTreeClassifier(min_samples_split=10)),
        2: ("Linear SVM", LinearSVC(verbose=1)),
        3: ("RBF SVM", SVC(C=10500, kernel="rbf", verbose=True, decision_function_shape="ovr")),
        4: ("Random Forest", RandomForestClassifier(verbose=3)),
        5: ("Neural Network", MLPClassifier(hidden_layer_sizes=(100,), early_stopping=True, verbose=True)),
        6: ("Gradient Boosting", GradientBoostingClassifier(verbose=1))}

#for t in range(len(target_options)):
for c in range(4,6):
    title = "{} by {}".format(target_options.get(t)[0], clfs.get(c)[0])
    sys.stdout = Logger(title)
    targets = target_options.get(t)[1]
    target_names = classes[np.unique(targets)]
    features_train, features_test, labels_train, labels_test = preprocess(word_data, targets)

    clf = clfs.get(c)[1]
    print("\n### CLASSIFICATION using {} ###".format(clfs.get(c)[0]))

    t0 = time()
    clf.fit(features_train, labels_train)
    print("Training time:", round((time()-t0)/60, 2), "m")
    joblib.dump(clf, "./data/{} Classifier.pkl".format(clfs.get(c)[0]))

    t1 = time()
    prediction = clf.predict(features_test.toarray())
    print("Prediction time:", round((time()-t1)/60, 2), "m")

    print(classification_report(labels_test, prediction, target_names=target_names))
    print("Accuracy:", accuracy_score(prediction, labels_test))

    cnf_matrix = confusion_matrix(labels_test, prediction)
    plot_confusion_matrix(cnf_matrix, target_names, title, show=False)
