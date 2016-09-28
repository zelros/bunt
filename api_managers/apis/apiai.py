# -*- coding: utf-8 -*-
from api import ApiManager
from urllib import quote

import logging
import requests
import time


class ApiAiException(Exception):
    def __init__(self, status):
        self.code = status['code']
        self.error_type = status.get('errorType')
        self.error_id = status.get('errorId')
        self.error_details = status.get('errorDetails')

    def __str__(self):
        return '[{code}/{error_type}] {error_details} ({error_id})'.format(
            code=self.code,
            error_type=self.error_type,
            error_id=self.error_id,
            error_details=self.error_details
        )


class ApiaiManager(ApiManager):
    def __init__(self, token, fallback_name, sleeping_time=3):
        ApiManager.__init__(self, fallback_name)
        logging.debug('[ApiAi] connect with token={token}'.format(token=token))

        self._base_url = 'https://api.api.ai/v1/'
        self._headers = {
            'Authorization': 'Bearer {0}'.format(token)
        }
        self._sleeping_time = sleeping_time

    def __repr__(self):
        return 'apiai'

    def fit(self, df_train):
        self._clear()
        X_train = df_train['sentence']
        y_train = df_train['intent']
        intents = set(y_train)
        for intent in intents:
            self._create_intent(intent, list(X_train[y_train == intent]), intent)
        self._create_intent(self._fallback_name, [], self._fallback_name, fallback=True)

        time.sleep(self._sleeping_time)

    def predict(self, x_list):
        predictions = []
        for i, x in enumerate(x_list):
            predictions.append(self._query(x)['action'])
        return predictions

    @classmethod
    def get_parametors(cls):
        return []

    def _clear(self):
        entities_name = self._get_intents().keys()
        for entity in entities_name:
            self._remove_intent_byname(entity)

    def _get_entities(self):
        logging.debug('[ApiAi] get_entities')

        r = requests.get(
            '{url}entities'.format(url=self._base_url),
            headers=self._headers,
        )

        result = r.json()

        if r.status_code != 200:
            raise ApiAiException(result['status'])

        return dict([(item['name'], item) for item in result])

    def _create_entity(self, name, entries):
        logging.debug('[ApiAi] create_entity: name={name}'.format(name=name))

        payload = {
            'name': name,
            'entries': entries,
        }

        r = requests.post(
            '{url}entities'.format(url=self._base_url),
            headers=self._headers,
            json=payload
        )

        result = r.json()

        if r.status_code != 200:
            raise ApiAiException(result['status'])

        return result['id']

    def _remove_entity_byid(self, entity_id):
        logging.debug('[ApiAi] remove_entity_byid: id={id}'.format(id=entity_id))

        r = requests.delete(
            '{url}entities/{id}'.format(url=self._base_url, id=entity_id),
            headers=self._headers,
        )

        result = r.json()

        if r.status_code != 200:
            raise ApiAiException(result['status'])

    def _remove_entity_byname(self, name):
        logging.debug('[ApiAi] remove_entity_byname: name={name}'.format(name=name))

        entities = self._get_entities()
        entity = entities.get(name)
        if entity:
            self._remove_entity_byid(entity['id'])

    def _create_entity_formated(self, name, values):
        logging.debug('[ApiAi] create_entity_formated: name={name}'.format(name=name))

        entities_entries = [{
                                'value': quote(value).lower(),
                                'synonyms': [value]
                            } for value in values]

        return self._create_entity(name, entities_entries)

    def _get_intents(self):
        logging.debug('[ApiAi] get_intents')

        r = requests.get(
            '{url}intents'.format(url=self._base_url),
            headers=self._headers,
        )

        result = r.json()

        if r.status_code != 200:
            raise ApiAiException(result['status'])

        return dict([(item['name'], item) for item in result])

    def _create_intent(self, name, templates, action, parameters=None, fallback=False):
        logging.debug('[ApiAi] create_intent: name={name}'.format(name=name))

        payload = {
            'name': name,
            'templates': templates,
            'responses': [
                {
                    'action': action,
                    'parameters': parameters,
                },
            ],
            'auto': True,
            'fallbackIntent': fallback,
            'state': 'LEARNED'
        }

        r = requests.post(
            '{url}intents'.format(url=self._base_url),
            headers=self._headers,
            json=payload
        )

        result = r.json()

        if r.status_code != 200:
            raise ApiAiException(result['status'])

        return result['id']

    def _remove_intent_byid(self, entity_id):
        logging.debug('[ApiAi] remove_intent_byid: id={id}'.format(id=entity_id))

        r = requests.delete(
            '{url}intents/{id}'.format(url=self._base_url, id=entity_id),
            headers=self._headers,
        )

        result = r.json()

        if r.status_code != 200:
            raise ApiAiException(result['status'])

    def _remove_intent_byname(self, name):
        logging.debug('[ApiAi] remove_intent_byname: name={name}'.format(name=name))

        intents = self._get_intents()
        intent = intents.get(name)
        if intent:
            self._remove_intent_byid(intent['id'])

    def _query(self, q):
        logging.debug(u'[ApiAi] query: q={q}'.format(q=q))

        payload = {
            'query': q,
            'lang': 'en',
        }

        r = requests.post(
            '{url}query'.format(url=self._base_url),
            headers=self._headers,
            json=payload
        )

        result = r.json()

        if r.status_code != 200:
            raise ApiAiException(result['status'])

        return result['result']
