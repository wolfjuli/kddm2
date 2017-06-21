#!/usr/bin/python

from preprocess import preprocess
from parse_emails import *
from helper_functions import Logger
from KerasMLP import KerasMLP

from time import time
import numpy as np
from pandas import DataFrame
from itertools import compress
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.externals import joblib

from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier

def init_classification_data():
    try:
        with open("./data/authors.pkl", "rb") as authors_file, \
                open("./data/word_data.pkl", "rb") as words_file, \
                open("./data/recipients.pkl", "rb") as recipients_file, \
                open("./data/classes.pkl", "rb") as classes_file:
            authors = np.array(pickle.load(authors_file))
            recipients = np.array(pickle.load(recipients_file))
            word_data = pickle.load(words_file)
            classes = np.array(pickle.load(classes_file))
    except Exception as e:
        print("Error in loading prepared data: {}\n Parsing data from database.".format(e))
        word_data, authors, recipients, classes = parse_mails()


    target_options = {0: ("Authors", authors),
                      1: ("Recipients", recipients),
                      2: ("AuthorsAndRecipients", zip(authors, recipients))}

    return word_data, target_options, classes


def init_classifiers():
    clfs = {0: ("Naive Bayes", MultinomialNB()),
            1: ("Decision Tree", DecisionTreeClassifier(min_samples_split=10)),
            2: ("Linear SVM", LinearSVC(verbose=1)),
            3: ("RBF SVM", SVC(C=10500, kernel="rbf", verbose=True, decision_function_shape="ovr")),
            4: ("Random Forest", RandomForestClassifier(verbose=3)),
            5: ("Neural Network", MLPClassifier(hidden_layer_sizes=(300,), early_stopping=True, verbose=True)),
            6: ("Gradient Boosting", GradientBoostingClassifier(verbose=1)),
            7: ("Keras MLP (TF GPU Support)", KerasMLP(hidden_layer_sizes=(100,), batch_size=10))}

    return clfs


def load_classifier(classifier, X, y):
    try:
        return joblib.load("./data/{} Classifier.pkl".format(classifier[0]))
    except:
        try:
            return KerasMLP.load("./data/{} Classifier".format(classifier[0]))
        except:
            return classify(classifier, y, X, save=True)


def classify(c, t, word_data, save=False):
    targets, clf = t[1], c[1]
    target_names = class_labels[np.unique(targets)]
    if len(target_names) == 1: return _, 1
    features_train, features_test, labels_train, labels_test = preprocess(word_data, targets)

    print("\n### CLASSIFICATION using {} ###".format(c[0]))
    t0 = time()
    clf.fit(features_train.toarray(), labels_train)
    print("Training time:", round((time()-t0)/60, 2), "m")

    t1 = time()
    prediction = clf.predict(features_test.toarray())
    print("Prediction time:", round((time()-t1)/60, 2), "m")

    print(classification_report(labels_test, prediction, target_names=target_names))
    acc = accuracy_score(prediction, labels_test)
    print("Accuracy:", acc)

    cm = np.nan_to_num(confusion_matrix(labels_test, prediction))
    norm_cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    score = np.diag(norm_cm)
    if save:
        try:
            joblib.dump((clf, score), "./data/{} Classifier.pkl".format(c[0]))
        except:
            clf.save("./data/{} Classifier".format(c[0]), score)
        plot_confusion_matrix(norm_cm, target_names, title, show=False)

    return clf, score


# CONFIGURATION
t = 2
c = 0
save_results = True

X, y_options, class_labels = init_classification_data()
y = y_options.get(t)
clfs = init_classifiers()

#for t in range(len(target_options)):
#for c in range(4,6):
title = "{} by {}".format(y[0], clfs.get(c)[0])
if save_results:
    sys.stdout = Logger(title)

if t == 2:
    authors = y_options.get(0)[1]
    recipients = y_options.get(1)[1]
    accuracies = []
    results = {}
    clf, author_score = load_classifier(clfs.get(7), X, y_options.get(0))

    for a in np.unique(authors):
        s_targets = list(compress(recipients, authors == a))
        s_data = list(compress(X, authors == a))
        _, score = classify(clfs.get(c), ("Recipients of {}".format(class_labels[a]), s_targets), s_data)
        accuracies.append(np.mean(score))
        results[a] = dict(zip(np.unique(s_targets), np.atleast_1d(score)))

    df = DataFrame(results).T
    plot_accuracy_matrix(df, class_labels[np.unique(recipients)], class_labels[np.unique(authors)], title)

    df = df.T.fillna(df.mean(axis=1)).T
    plot_accuracy_matrix(df, class_labels[np.unique(recipients)], class_labels[np.unique(authors)], title+" (filled)")
    print("##################################")
    print("Mean Recipient Score: {}".format(np.mean(accuracies)))
    print("##################################")
    print("FINAL SCORE: {}".format(np.mean(author_score * np.mean(accuracies))))
    print("##################################")

else:
    classify(clfs.get(c), y, X, save=save_results if t == 0 else False)

