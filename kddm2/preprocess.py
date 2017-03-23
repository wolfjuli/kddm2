#!/usr/bin/python

from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif, SelectKBest
import numpy as np


def preprocess(word_data, authors):
    print "\n### PREPROCESSING DATA ###"

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
    features_test_selected = selector.transform(features_test_transformed)#.toarray()

    #top_ranked_features = sorted(enumerate(selector.scores_),key=lambda x:x[1], reverse=True)
    #top_ranked_features_indices = map(list,zip(*top_ranked_features))[0]
    #for feature_pvalue in zip(np.asarray(vectorizer.get_feature_names())[top_ranked_features_indices],
    #                          selector.pvalues_[top_ranked_features_indices]):
    #    print feature_pvalue
    #print selector.scores_
    #print selector.get_support(indices=True)
    #id_word_dict = {y:x for x,y in vectorizer.vocabulary_.items()}
    #print [id_word_dict.get(i) for i in selector.get_support(indices=True)]

    # info on the data
    print "no. of Chris training emails:", sum(labels_train)
    print "no. of Sara training emails:", len(labels_train)-sum(labels_train)
    
    return features_train_selected, features_test_selected, labels_train, labels_test
