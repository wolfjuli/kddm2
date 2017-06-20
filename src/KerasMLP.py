import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from keras.callbacks import EarlyStopping
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from keras.models import model_from_json
import pickle as pkl

class KerasMLP:

    def __init__(self, hidden_layer_sizes=(100,), activation="relu", solver='adam', loss='categorical_crossentropy',
                 alpha=0.0001, epochs=100, early_stopping=True, batch_size=200):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.solver = solver
        self.loss = loss
        self.alpha = alpha
        self.epochs = epochs
        self.early_stopping = early_stopping
        self.batch_size = batch_size

    def _model(self):
        model = Sequential()
        for n in self.hidden_layer_sizes:
            model.add(Dense(n, input_dim=self.input_shape, activation=self.activation))
        model.add(Dense(self.output_shape, activation='softmax'))
        model.compile(loss=self.loss, optimizer=self.solver, metrics=['accuracy'])
        return model

    def fit(self, X, y):
        y = np_utils.to_categorical(y)
        self.input_shape = X.shape[1]
        self.output_shape = y.shape[1]

        self.model = self._model()
        callbacks = []
        if self.early_stopping:
            callbacks.append(EarlyStopping(monitor='val_loss', patience=2, verbose=0, mode='auto'))

        self.model.fit(X, y, validation_split=0.2 if self.early_stopping else 0,
                       nb_epoch=self.epochs, batch_size=self.batch_size,
                       callbacks=callbacks)

    def predict(self, X):
        predictions = self.model.predict_classes(X, batch_size=self.batch_size)
        return predictions

    def save(self, path, accuracy):
        with open("{}_arch.json".format(path), "w") as json_file:
            json_file.write(self.model.to_json())
        self.model.save_weights("{}_weights.hd5".format(path))
        with open("{}_acc.pkl".format(path), "wb") as acc_pkl:
            pkl.dump(np.array(accuracy), acc_pkl)

    @classmethod
    def load(cls, path):
        with open("{}_arch.json".format(path), "r") as json_file:
            json_model = json_file.read()
        model = model_from_json(json_model)
        model.load_weights("{}_weights.hd5".format(path))
        with open("{}_acc.pkl".format(path), "rb") as acc_pkl:
            accuracy = pkl.load(acc_pkl)
        return model, accuracy