# -*- coding: utf-8 -*-

from apis.apiai import ApiaiManager
from apis.luis import LuisManager
from apis.recast import RecastManager
from settings import credentials


def build_api(api_name, fallback_name, language, params):
    if api_name == 'apiai':
        return ApiaiManager(token=credentials.APIAI_TOKENS[language], fallback_name=fallback_name, **params)
    if api_name == 'luis':
        if language == 'en':
            return LuisManager(credentials.LUIS_KEY, fallback_name, 'en-us', **params)
        elif language == 'fr':
            return LuisManager(credentials.LUIS_KEY, fallback_name, 'fr-fr', **params)
    if api_name == 'recast':
        return RecastManager(credentials.RECAST_USER_SLUG, credentials.RECAST_BOT_SLUG, credentials.RECAST_TOKEN,
                             language, fallback_name, **params)


def check_params(api_name, params):
    api_class = None
    if api_name == 'recast':
        api_class = RecastManager
    elif api_name == 'apiai':
        api_class = ApiaiManager
    elif api_name == 'luis':
        api_class = LuisManager

    api_parameters = api_class.get_parametors()

    for parameter in params:
        if parameter not in api_parameters:
            raise Exception(' \'{}\' is not a parameter of {}'.format(parameter, api_name))
