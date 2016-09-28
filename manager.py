# -*- coding: utf-8 -*-

from api_managers import api_builder
from tools.comparator import Comparator
from tools.parametor import Parametor
from tools.scorer import Scorer
from tools import loader
from settings import settings

import json
import logging
import operator
import os

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self._comparator = None
        self._parametor = None
        self._scorer = Scorer(self, settings.METRICS, settings.FALLBACK_NAME)
        self._clean_logs()

    def compare(self):
        self._check_comparator_settings()
        self._comparator = Comparator(settings.CRITERIA, settings.APIS, self._scorer,
                                      settings.FALLBACK_NAME)
        self._comparator.compare()
        results = self._comparator.results
        with open(settings.COMPARATOR_RESULT_FILE, 'wb') as f:
            f.write(json.dumps(results))

    def score_parameters(self):
        self._check_parametor_settings()
        self._parametor = Parametor(settings.API, settings.CRITERIA, self._scorer, settings.FALLBACK_NAME)
        results = self._parametor.score_parameter_for_language(settings.PARAMS)
        results = self._show_parametor_results(results)
        with open(settings.PARAMETOR_RESULT_FILE, 'wb') as f:
            f.write(json.dumps(results))

    def log_success(self, api_name, sentence, intent_to_find):
        with open(settings.LOG_SUCCESS, 'a') as f:
            f.write(u'{}\t{}\t{}\n'.format(api_name, intent_to_find, sentence).encode('utf-8'))

    def log_fallback(self, api_name, sentence, intent_to_find):
        with open(settings.LOG_FALLBACK, 'a') as f:
            f.write(u'{}\t{}\t{}\n'.format(api_name, intent_to_find, sentence).encode('utf-8'))

    def log_error(self, api_name, sentence, intent_to_find, intent_found):
        with open(settings.LOG_ERROR, 'a') as f:
            f.write(u'{}\t{}\t{}\t{}\n'.format(api_name, intent_found, intent_to_find, sentence).encode('utf-8'))

    def _check_comparator_settings(self):
        self._check_general_settings()
        for api in settings.APIS:
            if api not in settings.APIS_HANDLED:
                raise Exception(
                    'The Api \'{}\' is not handled. Add it in settings.apis_handled if it is implemented'.format(api))

        comparator_result_file = settings.COMPARATOR_RESULT_FILE
        file_split = comparator_result_file.split('/')
        folder = '/'.join(file_split[:-1])
        if folder != 'data/results/comparator':
            raise Exception(
                'Your result file must be in data/results/comparator directory. Yours is in {}'.format(folder)
            )
        if os.path.isfile(comparator_result_file):
            logger.warn('Your result file already exists. It\'s content will be updated by the end of the execution')

    def _check_parametor_settings(self):
        self._check_general_settings()
        if settings.API not in settings.APIS_HANDLED:
            raise Exception(
                'The Api \'{}\' is not handled. Add it in settings.apis_handled if it is implemented'.format(
                    settings.API)
            )

        if settings.PARAMETOR_RESULT_MODE not in settings.PARAMETOR_RESULT_MODE_HANDLED:
            raise Exception('the result mode {} of parametor is not handled'.format(settings.PARAMETOR_RESULT_MODE))

        parametor_result_file = settings.PARAMETOR_RESULT_FILE
        file_split = parametor_result_file.split('/')
        folder = '/'.join(file_split[:-1])
        if folder != 'data/results/parametor':
            raise Exception(
                'Your result file must be in data/results/parametor directory. Yours is in {}'.format(folder)
            )
        if os.path.isfile(parametor_result_file):
            logger.warn('Your result file already exists. It\'s content will be updated by the end of the execution')
        api_builder.check_params(settings.API, settings.PARAMS)

    def _check_general_settings(self):
        for metric in settings.METRICS:
            if metric not in settings.METRICS_HANDLED:
                raise Exception(
                    'The metric \'{}\' is not handled. Add it in settings.metrics_handled if it is implemented')

        for language in settings.CRITERIA:
            for criterion in settings.CRITERIA[language]:
                loader.check_file(language, criterion)

    def _show_parametor_results(self, results):
        results = self.invert_metric_param(results)
        if settings.PARAMETOR_RESULT_MODE == 'all':
            return results
        elif settings.PARAMETOR_RESULT_MODE == 'best':
            return self._show_best_params(results)

        else:
            raise Exception('unknown mode {}'.format(settings.PARAMETOR_RESULT_MODE))

    def invert_metric_param(self, results):
        inverted_results = {}
        metrics = settings.METRICS
        for language in results:
            inverted_results[language] = {}
            for criterion in results[language]:
                inverted_results[language][criterion] = {}
                for metric in metrics:
                    inverted_results[language][criterion][metric] = {}

                for parameter_name in results[language][criterion]:
                    for parameter_value in results[language][criterion][parameter_name]:
                        for metric in metrics:
                            score = results[language][criterion][parameter_name][parameter_value][metric]
                            if parameter_name not in inverted_results[language][criterion][metric]:
                                inverted_results[language][criterion][metric][parameter_name] = {}
                            inverted_results[language][criterion][metric][parameter_name][parameter_value] = score
        return inverted_results

    def _show_best_params(self, results):
        best_params = {}
        for language in results:
            best_params[language] = {}
            for criterion in results[language]:
                best_params[language][criterion] = {}
                for metric in results[language][criterion]:
                    best_params[language][criterion][metric] = {}
                    for parameter_name in results[language][criterion][metric]:
                        values = results[language][criterion][metric][parameter_name]
                        best_params[language][criterion][metric][parameter_name] = \
                            max(values.iteritems(), key=operator.itemgetter(1))[0]
        return best_params

    def _clean_logs(self):
        with open(settings.LOG_SUCCESS, 'wb') as f:
            f.write('API\tINTENT\tSENTENCE\n')
        with open(settings.LOG_FALLBACK, 'wb') as f:
            f.write('API\tINTENT\tSENTENCE\n')
        with open(settings.LOG_ERROR, 'wb') as f:
            f.write('API\tINTENT_FOUND\tREAL_INTENT\tSENTENCE\n')
