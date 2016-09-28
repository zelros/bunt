# -*- coding: utf-8 -*-

from api_managers import api_builder
from tools import loader

import logging

logger = logging.getLogger(__name__)


class Comparator:
    def __init__(self, criteria, apis, scorer, fallback_name):
        self.criteria = criteria
        self.apis = apis
        self.scorer = scorer
        self.fallback_name = fallback_name
        self.results = {}

    def compare(self):
        results = {}
        logger.info('Comparator :')
        for language in self.criteria:
            logger.info('\tlanguage: {}'.format(language))
            results[language] = {}
            for criterion in self.criteria[language]:
                logger.info('\t\tcriterion: {}'.format(criterion))
                # get data_frame
                df = loader.load(language, criterion)
                logger.info('\t\t\tdata ready')

                results[language][criterion] = {}

                for api in self.apis:
                    api_manager = api_builder.build_api(api_name=api, fallback_name=self.fallback_name,
                                                        language=language, params={})
                    self.scorer.fit(api_manager, df)
                    logger.info('\t\t\tscoring {}'.format(api))
                    self.scorer.score()
                    results[language][criterion][str(api_manager)] = {'scores': self.scorer.scores,
                                                                      'risk_rate': self.scorer.risk_rate}

        self.results = results
