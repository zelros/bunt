# -*- coding: utf-8 -*-

from api_managers import api_builder
from tools import loader

import logging

logger = logging.getLogger(__name__)


class Parametor:
    def __init__(self, api, criteria, scorer, fallback_name):
        self.criteria = criteria
        self.api = api
        self.scorer = scorer
        self.fallback_name = fallback_name
        self.results = {}

    def _score_one_parameter(self, parameters, language, criterion, parameter_name):

        result = {}
        df = loader.load(language, criterion)

        for parameter_value in parameters:
            logger.info('\t\t\t{}={}'.format(parameter_name, parameter_value))
            builder_params = {parameter_name: parameter_value}
            api_manager = api_builder.build_api(api_name=self.api, fallback_name=self.fallback_name, language=language,
                                                params=builder_params)
            self.scorer.fit(api_manager, df)
            self.scorer.score()
            scores = self.scorer.scores
            result[parameter_value] = scores
        return result

    def _score_parameter_for_criterion(self, language, parameters, criterion):
        result = {}
        for parameter_name in parameters:
            logger.info('\t\tparameter: {}'.format(parameter_name))
            result[parameter_name] = self._score_one_parameter(parameters[parameter_name], language, criterion,
                                                               parameter_name)

        return result

    def score_parameter_for_language(self, parameters):
        logger.info('Parametor :')
        result = {}
        for language in self.criteria:
            logger.info('choosing best parameters language {}'.format(language))
            result[language] = {}
            for criterion in self.criteria[language]:
                logger.info('\t criterion: {}'.format(criterion))
                result[language][criterion] = self._score_parameter_for_criterion(language, parameters, criterion)

        return result
