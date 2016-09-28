# -*- coding: utf-8 -*-

from sklearn.cross_validation import train_test_split

import logging
import numpy as np

logger = logging.getLogger(__name__)


class Scorer:
    def __init__(self, manager, metrics, fallback_name, n_fold=5, test_size=0.3, random_state=42):
        self.manager = manager
        self.metrics = metrics
        self.fallback_name = fallback_name
        self.n_fold = n_fold
        self.test_size = test_size
        self.random_state = random_state
        self.scores = None
        self.api = None
        self.df = None
        self.risk_rate = None

    def fit(self, api, df, test_size=None, random_state=None):
        self.api = api
        self.df = df
        if test_size is not None:
            self.test_size = test_size
        if random_state is not None:
            self.random_state = random_state

    def score(self):
        scores = {}
        risk_rate = 0
        for metric in self.metrics:
            scores[metric] = []
        for i in range(self.n_fold):
            logger.info('\t\t\t\tscoring fold {}/{}'.format(i + 1, self.n_fold))
            df_train, df_test = train_test_split(self.df, test_size=self.test_size, random_state=self.random_state + i)
            self._fit(df_train)
            score_fold, risk_rate_fold = self._score_fold(self.df)
            risk_rate += risk_rate_fold
            for metric in self.metrics:
                scores[metric].append(score_fold[metric])
        risk_rate /= float(self.n_fold)
        for metric in self.metrics:
            logger.info('\t\t\t\tmetric {}: {}'.format(metric, np.mean(scores[metric])))
            scores[metric] = np.mean(scores[metric])
        self.scores = scores
        self.risk_rate = risk_rate

    def _score_fold(self, df_test):
        X_test = np.array(df_test['sentence'])
        y_test = np.array(df_test['intent'])

        n_found = 0
        n_fallback = 0
        n_error = 0

        for i, x in enumerate(X_test):
            intent_found = self.api.predict([x])[0]
            if intent_found.lower() == y_test[i].lower():
                n_found += 1
                self._log_success(sentence=x, intent_to_find=y_test[i])
            elif intent_found == self.fallback_name:
                self._log_fallback(sentence=x, intent_to_find=y_test[i])
                n_fallback += 1

            else:
                self._log_error(sentence=x, intent_to_find=y_test[i], intent_found=intent_found)
                n_error += 1
        logger.info('\t\t\t\t\t{} ok, {} fallback, {} errors'.format(n_found, n_fallback, n_error))
        scores = {}
        for metric in self.metrics:
            scores[metric] = self._score_metric(n_found, n_fallback, n_error, metric=metric)

        risk_rate = 1 - n_fallback / float(n_fallback + n_found + n_error)
        return scores, risk_rate

    def _score_metric(self, n_found, n_fallback, n_error, metric):
        if metric == 'accuracy':
            return n_found / float(n_found + n_fallback + n_error)

        if metric == 'error_3_penalized':
            # error counts for 3 errors
            return n_found / float(n_found + n_fallback + 3 * n_error)

        if metric == 'error_10_penalized':
            return n_found / float(n_found + n_fallback + 10 * n_error)

    def _fit(self, df_train):
        self.api.fit(df_train)

    def _log_success(self, sentence, intent_to_find):
        self.manager.log_success(str(self.api), sentence, intent_to_find)

    def _log_fallback(self, sentence, intent_to_find):
        self.manager.log_fallback(str(self.api), sentence, intent_to_find)

    def _log_error(self, sentence, intent_to_find, intent_found):
        self.manager.log_error(str(self.api), sentence, intent_to_find, intent_found)
