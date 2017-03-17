#!/usr/bin/python

from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif


def preprocess(word_data, authors):
    print "\n### PREPROCESSING DATA ###"

    # train and test split
    features_train, features_test, labels_train, labels_test = \
        cross_validation.train_test_split(word_data, authors, test_size=0.1, random_state=42)

    # vectorize
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5)  # , stop_words='english'
    features_train_transformed = vectorizer.fit_transform(features_train)
    features_test_transformed  = vectorizer.transform(features_test)

    # feature selection
    selector = SelectPercentile(f_classif, percentile=10)
    features_train_transformed = selector.fit_transform(features_train_transformed, labels_train)
    features_test_transformed  = selector.transform(features_test_transformed).toarray()

    # info on the data
    print "no. of Chris training emails:", sum(labels_train)
    print "no. of Sara training emails:", len(labels_train)-sum(labels_train)
    
    return features_train_transformed, features_test_transformed, labels_train, labels_test
