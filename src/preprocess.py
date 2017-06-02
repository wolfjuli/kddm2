#!/usr/bin/python

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif, SelectKBest
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


def preprocess(word_data, targets):
    print("\n### PREPROCESSING DATA ###")
    # train and test split
    try:
        features_train, features_test, labels_train, labels_test = \
            train_test_split(word_data, targets, test_size=0.2, stratify=targets)
    except:
        features_train, features_test, labels_train, labels_test = \
            train_test_split(word_data, targets, test_size=0.2)

    # vectorize
    print("-- Vectorization")
    vectorizer = TfidfVectorizer(sublinear_tf=True)  # , stop_words='english'
    features_train_transformed = vectorizer.fit_transform(features_train)
    features_test_transformed = vectorizer.transform(features_test)

    # feature selection
    print("-- Feature Selection")
    selector = SelectPercentile(percentile=10)
    # selector = SelectKBest(k=100)
    features_train_selected = selector.fit_transform(features_train_transformed, labels_train)
    print(features_train_selected.shape)
    features_test_selected = selector.transform(features_test_transformed)

    # print top features
    nr_features = 30
    i = selector.scores_.argsort()[::-1][:nr_features]
    top_features = np.column_stack((np.asarray(vectorizer.get_feature_names())[i],
                                    selector.scores_[i],
                                    selector.pvalues_[i]))
    print("\nTop %i Features:" % nr_features)
    print(pd.DataFrame(top_features, columns=["token", "score", "p-val"]), "\n")
    
    return features_train_selected, features_test_selected, labels_train, labels_test
