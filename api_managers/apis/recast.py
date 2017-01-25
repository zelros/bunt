# -*- coding: utf-8 -*-

#  https://man.recast.ai/
from api import ApiManager

import requests


class RecastManager(ApiManager):
    def __init__(self, user_slug, bot_slug, token, language, fallback_name, strictness=50):
        ApiManager.__init__(self, fallback_name)
        self._base_url = 'https://api.recast.ai/v2'
        self._user_slug = user_slug
        self._bot_slug = bot_slug
        self.strictness = strictness
        self._url = '{0}/users/{1}/bots/{2}'.format(self._base_url, user_slug, bot_slug)
        self._token = token
        self._headers = {
            'Authorization': 'Token {}'.format(self._token)
        }
        self._language = language
        self._update_bot()

    def __repr__(self):
        return 'recast'

    def predict(self, sentences):
        predictions = []
        for sentence in sentences:
            predictions.append(self._predict_one(sentence))
        return predictions

    def fit(self, df_train):
        self._clear()
        X_train = df_train['sentence']
        y_train = df_train['intent']
        intents = set(y_train)
        for intent in intents:
            utterances = list(X_train[y_train == intent])
            self._create_intent(intent, utterances, self._language)

    @classmethod
    def get_parametors(cls):
        return ['strictness']

    def _update_bot(self):

        response = requests.put(
            url='{}'.format(self._url),
            json={
                'name': self._bot_slug,
                'strictness': self.strictness
            },
            headers=self._headers
        )
        return response

    def _create_intent(self, name, expressions, language, description='', n_try=0):

        array = []
        for expression in expressions:
            array.append(
                {
                    'source': expression,
                    'language': {'isocode': language}

                }
            )

        response = requests.post(
            url='{}/intents'.format(self._url),
            json={
                'name': name,
                'description': description,
                'expressions': array
            },
            headers=self._headers
        )

        try:
            return response.json()
        except:
            if n_try < 3:
                return self._create_intent(name, expressions, language, '', n_try=n_try + 1)
            raise Exception('no json could be decoded')

    def _clear(self):
        intent_slugs = self._get_intents_slug()
        for slug in intent_slugs:
            self._delete_intent_by_slug(slug)

    def _delete_intent_by_slug(self, intent_slug):

        response = requests.delete(
            url='{}/intents/{}'.format(self._url, intent_slug),
            headers=self._headers
        )
        return response.json()

    def _get_intents_slug(self):

        response = requests.get(
            url='{}/intents'.format(self._url),
            # url = 'https://api.recast.ai/v1/users/pytha/bots/test/intents',
            headers=self._headers
        )

        response = response.json()
        intents = response['results']

        intent_slugs = []
        for intent in intents:
            intent_slugs.append(intent['slug'])
        return intent_slugs

    def _predict_one(self, sentence):

        response = requests.post(
            url='{}/request'.format(self._base_url),
            data={
                'text': sentence,
                'language': self._language
            },
            headers=self._headers
        )
        response = response.json()

        if len(response['results']['intents']) > 0:
            return response['results']['intents'][0]['slug']
        return self._fallback_name
