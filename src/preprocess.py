#!/usr/bin/python

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif, SelectKBest
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import pickle

def preprocess(word_data, targets):
    print("\n### PREPROCESSING DATA ###")

    # vectorize
    print("-- Vectorization")
    vectorizer = TfidfVectorizer(sublinear_tf=True)  # , stop_words='english'
    data_transformed = vectorizer.fit_transform(word_data)

    # feature selection
    print("-- Feature Selection")
    selector = SelectPercentile(percentile=5)
    # selector = SelectKBest(k=100)
    data_selected = selector.fit_transform(data_transformed, targets)
    print("Top {} features were selected".format(data_selected.shape[1]))

    # print top features
    nr_features = 30
    i = selector.scores_.argsort()[::-1][:nr_features]
    top_features = np.column_stack((np.asarray(vectorizer.get_feature_names())[i],
                                    selector.scores_[i],
                                    selector.pvalues_[i]))
    print("\nTop %i Features:" % nr_features)
    print(pd.DataFrame(top_features, columns=["token", "score", "p-val"]), "\n")

    # train and test split
    try:
        features_train, features_test, labels_train, labels_test = \
            train_test_split(data_selected, targets, test_size=0.2, stratify=targets)
    except:
        features_train, features_test, labels_train, labels_test = \
            train_test_split(data_selected, targets, test_size=0.2)

    pickle.dump((features_train, features_test, labels_train, labels_test),
                open("./data/preprocessed data.pkl", "wb"))
    return features_train, features_test, labels_train, labels_test
