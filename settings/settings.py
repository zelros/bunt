# -*- coding: utf-8 -*-

from logging.config import dictConfig
from requests.packages.urllib3 import disable_warnings

"""
____________________________________________
*************General setting*************
____________________________________________
ACTION:
    action that should do the program.
    the available actions are 'comparator' and 'parametor'

METRICS:
    list of all the scoring rules.

CRITERIA:
    Dictionary.
    Keys are the languages of all criteria.
    Values are the name of the file containing the data used to define the criterion

API_HANDLED:
    list of the names of the apis available.
    Please edit this list if you want to add yours

FALLBACK_NAME:
    name of the fallback intent.
    Should not be edited except if an intent of your data_set has the same name

LOG_SUCCESS:
    path to the file where the queries which have been answered with the good intents will be logged

LOG_ERROR:
    path to the file where the queries which have not been answered with the good intents will be logged

LOG_FALLBACK:
    path to the file where the queries which the api did not provide any intent will be logged


____________________________________________
*************Comparator setting*************
____________________________________________

APIS:
    list of the names of the apis you want to compare

COMPARATOR_RESULT_FILE:
    path to the file where the results will be written.
    If the file does not exist in the directory, it will be created
    The program will erase any former content of the file
____________________________________________
*************Parametor setting*************
____________________________________________

API:
    name of the api you want to tune the parameters

PARAMS:
    dictionnary.
    Keys : parameters to tune
    Values : list of the values of the parameter to try

RESULTS_MODE:
    way to show the results. Defaults to 'all'
    if all : return the score obtained for each value of the parameters tested
    if best: return only the best parameters

PARAMETOR_RESULT_FILE :
    path to the file where the results will be written.
    If the file does not exist in the directory, it will be created
    The program will erase any former content of the file

"""

ACTION = 'comparator'
METRICS = ['error_10_penalized', 'error_3_penalized', 'accuracy']
CRITERIA = {
    'en': ['smalltalk_en', 'mails_en', 'misspellings_en', 'usual_things_en'],
    'fr': ['smalltalk_fr', 'mails_fr', 'misspellings_fr', 'usual_things_fr']
}

FALLBACK_NAME = 'fallback_not_understood'

APIS_HANDLED = ['apiai', 'recast', 'luis']
METRICS_HANDLED = ['error_10_penalized', 'error_3_penalized', 'accuracy']
PARAMETOR_RESULT_MODE_HANDLED = ['all', 'best']
# logging
LOG_SUCCESS = 'data/logs/log_success.csv'
LOG_ERROR = 'data/logs/log_error.csv'
LOG_FALLBACK = 'data/logs/log_fallback.csv'

"""
___________________________________________________________________________________________

Comparator
___________________________________________________________________________________________
"""
APIS = ['apiai, recast, luis']
COMPARATOR_RESULT_FILE = 'data/results/comparator/all_results.json'

"""
___________________________________________________________________________________________

Parametor
___________________________________________________________________________________________
"""
PARAMS = {
    'strictness': [0, 25, 50, 75, 100]
}
PARAMETOR_RESULT_MODE = 'all'
PARAMETOR_RESULT_FILE = 'data/results/parametor/result.json'

API = 'recast'


dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(asctime)-6s: %(levelname)s - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
    },
    'loggers': {
        'requests': {
            'level': 'ERROR',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
})

# Disable HTTPS warning
disable_warnings()
