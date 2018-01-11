import random
import pandas
from pandas.util.testing import assert_series_equal

import warnings
import logging

import sklearn.exceptions
from sklearn.metrics import *
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import *
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

import src.FeatureManager as fm
import src.Utils as Utils

logging.basicConfig(level=logging.ERROR)

warnings.filterwarnings("ignore", category=sklearn.exceptions.UndefinedMetricWarning)


# form sklearn.model_selection import GridSearchCV

def filter_dataframe_by_handwriting(dataframe, classes, user_data, handwriting):
    temp = dataframe.join(classes).join(user_data[Utils.HANDWRITING], on=Utils.USER_ID).drop(Utils.USER_ID, axis=1)
    return temp[temp[Utils.HANDWRITING] == handwriting].drop(Utils.HANDWRITING, axis=1)


def filter_classes_by_handwriting(classes, user_data, handwriting):
    temp = pandas.DataFrame(classes).join(user_data[Utils.HANDWRITING], on=Utils.USER_ID)
    return temp[temp[Utils.HANDWRITING] == handwriting].drop(Utils.HANDWRITING, axis=1).squeeze()


def filter_by_handwriting(dataframe, classes, user_data, handwriting):
    return (filter_dataframe_by_handwriting(dataframe, classes, user_data, handwriting),
            filter_classes_by_handwriting(classes, user_data, handwriting))


def get_most_common_priority(list):
    seen = []
    max_value = 0

    for x in list:
        count_x = sum(1 if x == y else 0 for y in list)
        if count_x > max_value:
            max_value = count_x
        if x not in [a[0] for a in seen]:
            seen.append((x, count_x))

    for x, count in seen:
        if max_value == count:
            return x




if __name__ == '__main__':
    f = fm.FeaturesManager(Utils.DATASET_NAME_0)

    for h in [Utils.ITALIC, Utils.BLOCK_LETTER]:

        print("...............................", h, "...................................")
        y = f.get_classes()
        user_data = f.get_classes_data()

        predictions = {}
        X_train = {}
        y_train = {}
        X_test = {}
        y_test = {}
        a = None
        r = random.randint(0, 100000)



        # Set the parameters by cross-validation
        tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4, 1e-2, 1e-1, 1e-5], 'C': [0.1, 1, 10, 100, 500, 1000,  2500, 5000, 7500,10000]},
                            {'kernel': ['linear'], 'C': [0.1, 1, 10, 100, 500, 1000, 2500, 5000, 7500,10000]}]
                            #{'kernel': ['poly'], 'C': [1, 10, 100, 1000], 'degree':[2, 3, 4, 5, 6], 'gamma': [1e-3, 1e-4]}]
        scoring = ['precision_macro', 'recall_macro', 'f1_macro']

        # for label in Utils.TIMED_POINTS_SERIES_TYPE:
        #     x = f.get_features()[label]
        #     x, y = filter_by_handwriting(x, y, user_data, h)
        #     X_train[label], X_test[label], y_train[label], y_test[label] = train_test_split(x, y, random_state=r,
        #                                                                                     test_size=0.3)
        #     scaler = StandardScaler()
        #     x = scaler.fit(X_train[label])
        #     X_train[label] = scaler.transform(X_train[label])
        #     X_test[label] = scaler.transform(X_test[label])

        assert_series_equal(y_train[Utils.MOVEMENT_POINTS], y_train[Utils.TOUCH_UP_POINTS])
        assert_series_equal(y_train[Utils.TOUCH_DOWN_POINTS], y_train[Utils.TOUCH_UP_POINTS])

        for label in Utils.TIMED_POINTS_SERIES_TYPE:
            print("Testing on: " + label)
            classifier = GridSearchCV(SVC(), tuned_parameters, scoring=scoring, cv=5, refit='f1_macro', n_jobs=-1)
            classifier = classifier.fit(X_train[label], y_train[label])
            predictions[label] = classifier.predict(X_test[label])
            print("Best parameters set found on development set:")
            print()
            print(classifier.best_params_)
            print(classifier.best_score_)
            print(classifier.best_estimator_)
            print(classifier.scorer_)
            # print(pandas.DataFrame(classifier.cv_results_).to_string())
            # print("Grid scores on development set:")
            # print()
            # means = classifier.cv_results_['mean_test_score']
            # stds = classifier.cv_results_['std_test_score']
            # for mean, std, params in zip(means, stds, classifier.cv_results_['params']):
            #     print("%0.3f (+/-%0.03f) for %r"
            #           % (mean, std * 2, params))
            print()
            y_true, y_pred = y_test[label], classifier.predict(X_test[label])
            print(classification_report(y_true, y_pred))
            print()

        # todo va fatto per ogni direzione di split
        mixed_pre = []
        print("Testing on: majority results")
        for a, b, c in zip(predictions[Utils.MOVEMENT_POINTS], predictions[Utils.TOUCH_UP_POINTS], predictions[Utils.TOUCH_DOWN_POINTS]):
            mixed_pre.append(get_most_common_priority([a, b, c]))
        print(classification_report(y_test[Utils.MOVEMENT_POINTS], mixed_pre))