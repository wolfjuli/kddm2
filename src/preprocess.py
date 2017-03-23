#!/usr/bin/python

from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif, SelectKBest
import numpy as np
import pandas as pd


def preprocess(word_data, authors):
    print "\n### PREPROCESSING DATA ###\n"

    # train and test split
    features_train, features_test, labels_train, labels_test = \
        cross_validation.train_test_split(word_data, authors, test_size=0.2, random_state=42)

    # vectorize
    vectorizer = TfidfVectorizer(sublinear_tf=True)  # , stop_words='english'
    features_train_transformed = vectorizer.fit_transform(features_train)
    features_test_transformed = vectorizer.transform(features_test)

    # feature selection
    selector = SelectPercentile(percentile=10)
    #selector = SelectKBest(k=100)
    features_train_selected = selector.fit_transform(features_train_transformed, labels_train)
    features_test_selected = selector.transform(features_test_transformed)

    # print top features
    nr_features = 10
    i = selector.scores_.argsort()[::-1][:nr_features]
    top_features = np.column_stack((np.asarray(vectorizer.get_feature_names())[i],
                                    selector.scores_[i],
                                    selector.pvalues_[i]))
    print "Top %i Features:" % nr_features
    print pd.DataFrame(top_features, columns=["token", "score", "p-val"]), "\n"

    # info on the data
    print "no. of Chris training emails:", sum(labels_train)
    print "no. of Sara training emails:", len(labels_train)-sum(labels_train)
    
    return features_train_selected, features_test_selected, labels_train, labels_test
