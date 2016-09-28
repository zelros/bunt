# -*- coding: utf-8 -*-


class ApiManager:
    def __init__(self, fallback_name):
        """
        Initialize the manager of the Api. Should keep in memory the fallback_name
        :param fallback_name:
            name of the intent to return in fallback case.
        """
        self._fallback_name = fallback_name

    def __repr__(self):
        """
        should return the same name as written in settings file
        """
        raise NotImplementedError('the name of the Api should be given in __repr__')

    def fit(self, df_train):
        """
        By applying fit function, the API must :
            - forget former intents & entities
            - update intents & entities
            - train its model
            - be available from http requests (for predictions)
                (some apis like Luis must be 'published' here

        :param
            - df_train: Pandas DataFrame
                DataFrame containing the intents and some examples of sentences for each intent.
                The name of the columns are 'sentence' and 'intent'
                You may want to separate the intents and the sentences as done below:
                X_train = df_train['sentence']
                y_train = df_train['intent']

        :return: void
        """
        raise NotImplementedError('fit method has not been implemented')

    def predict(self, sentences_list):
        """
        Given a list of sentences, this function must return the list of intents relative to the sentences.
        :param
            sentences_list: list
                list of the sentences you want to get the intent
        :return:
            list of the intents
        """
        raise NotImplementedError('predict method has not been implemented')

    @classmethod
    def get_parametors(cls):
        """
        This class method must return the list of all the parameters the user can set.
        These parameters must be configurable from the constructor function

        :return:
            list of parameters

        """
        raise NotImplementedError('get_parametors class method has not been implemented')
