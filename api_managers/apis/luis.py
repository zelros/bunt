# -*- coding: utf-8 -*-

# https://dev.projectoxford.ai/docs/services/56d95961e597ed0f04b76e58/operations/56f8a55119845511c81de488
from api import ApiManager

import json
import requests
import time


class LuisManager(ApiManager):
    def __init__(self, key, fallback_name, language='en-us', app_id=None):
        ApiManager.__init__(self, fallback_name)
        self._key = key
        self._language = language
        self._app_id = app_id
        if app_id is not None:
            self._api = ApiLuis(self._key, self._app_id)
        else:
            self._api = None

    def __repr__(self):
        return 'luis'

    def fit(self, df_train):
        self._clear()
        X_train = df_train['sentence']
        y_train = df_train['intent']
        intents = set(y_train)
        for intent in intents:
            utterances = list(X_train[y_train == intent])
            self._api.create_intent_with_utterances(intent, utterances)

        self._api.train()
        while not self._api.is_trained():
            time.sleep(1)
        self._publish()

    def predict(self, x_list):
        predictions = []
        for i, x in enumerate(x_list):
            intent = self._api.query(x)
            if intent == 'None':
                intent = self._fallback_name
            predictions.append(intent)
        return predictions

    @classmethod
    def get_parametors(cls):
        return []

    def _clear(self):
        if self._api is not None:
            self._delete_app()
        self._create_app(app_name='luis_app', lang=self._language)

    def _create_app(self, app_name, lang='en-us'):
        url = 'https://api.projectoxford.ai/luis/v1.0/prog/apps?subscription-key={0}'.format(self._key)
        payload = {
            "Name": app_name,
            "Culture": lang,
            "Active": True,
            "NumberOfIntents": 0,
            "NumberOfEntities": 0,
            "IsTrained": True
        }
        resp = requests.post(url=url, data=payload)
        app_id = resp.json()
        self._app_id = app_id
        self._api = ApiLuis(self._key, app_id)
        return app_id

    def _delete_app(self, appIdGiven=None):

        if appIdGiven is None:
            # delete own app
            appId = self._app_id
        else:
            appId = appIdGiven
        url = 'https://api.projectoxford.ai/luis/v1.0/prog/apps/{0}?subscription-key={1}'.format(
            appId, self._key)
        resp = requests.delete(url=url)
        if appIdGiven == self._app_id:
            self._app_id = None
            self._api = None
        return resp

    def _publish(self, appIdGiven=None):

        if appIdGiven is None:
            appId = self._app_id
        else:
            appId = appIdGiven

        url = 'https://api.projectoxford.ai/luis/v1.0/prog/apps/{0}/publish?subscription-key={1}'.format(
            appId, self._key)
        resp = requests.post(url=url)
        return resp


class ApiLuis(object):
    def __init__(self, key, appId):
        self._base_url = "https://api.projectoxford.ai/luis/"
        self._key = key
        self._app_id = appId

    def get_intents(self, intent_type='name'):
        """
        :param intent_type: 'id' ou 'name'
        :return: intents
        """
        url = '{0}v1.0/prog/apps/{1}/intents'.format(self._base_url, self._app_id)
        params = {
            'subscription-key': self._key
        }
        resp = requests.get(url=url, params=params)
        resp = resp.json()
        intents = []
        for intent in resp:
            intents.append(intent[intent_type])
        return intents

    def query(self, txt, retry=2):
        url = '{0}v1/application'.format(self._base_url)
        params = {
            'id': self._app_id,
            'subscription-key': self._key,
            'q': txt
        }
        resp = requests.get(url=url, params=params)
        resp = resp.json()
        try:
            return resp['intents'][0]['intent']
        except Exception as err:
            if retry > 0:
                return self.query(txt, retry - 1)
            else:
                raise err

    def create_intent(self, name, retry=2):
        url = '{0}v1.0/prog/apps/{1}/intents?&subscription-key={2}'.format(self._base_url, self._app_id, self._key)

        data = {
            'Name': name,
            'Children': {}
        }
        resp = requests.post(url=url, data=json.dumps(data))
        try:
            return resp.json()
        except ValueError as err:
            if retry > 0:
                return self.create_intent(name, retry - 1)
            else:
                raise err

    def get_id_intent(self, name_intent):
        url = '{0}v1.0/prog/apps/{1}/intents'.format(self._base_url, self._app_id)
        params = {
            'subscription-key': self._key
        }
        resp = requests.get(url=url, params=params)
        resp = resp.json()
        for intent in resp:
            if intent['name'].lower() == name_intent.lower():
                return intent['id']
        return None

    def delete_intent_byid(self, intent_id):
        url = '{0}v1.0/prog/apps/{1}/intents/{2}?&subscription-key={3}'.format(
            self._base_url, self._app_id, intent_id, self._key)

        resp = requests.delete(url)
        return resp

    def delete_intent_byname(self, name):
        intent_id = self.get_id_intent(name)
        return self.delete_intent_byid(intent_id)

    def train(self):
        url = '{0}v1.0/prog/apps/{1}/train?&subscription-key={2}'.format(self._base_url, self._app_id, self._key)
        resp = requests.post(url)
        return resp

    def is_trained(self):
        url = '{0}v1.0/prog/apps/{1}/train?&subscription-key={2}'.format(self._base_url, self._app_id, self._key)
        resp = requests.get(url)
        resp = resp.json()
        for model in resp:
            if model['Details']['Status'] not in ['Success', 'Up to date']:
                return False
        return True

    def new_utterance(self, intent_name, uterrance):
        url = '{0}v1.0/prog/apps/{1}/example?&subscription-key={2}'.format(self._base_url, self._app_id, self._key)
        payload = {
            "ExampleText": uterrance,
            "SelectedIntentName": intent_name,
            "EntityLabels": {}
        }
        resp = requests.post(url=url, data=payload)
        return resp

    def create_intent_with_utterances(self, name, uterrances):
        """

        :param name: name of the intent
        :param uterrances: list of intents
        :return: response of request
        """

        self.create_intent(name=name)
        for utter in uterrances:
            self.new_utterance(intent_name=name, uterrance=utter)
