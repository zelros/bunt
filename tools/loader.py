# -*- coding: utf-8 -*-

import os
import pandas as pd


def check_file(language, criterion):
    data_file = 'data/criteria/{}/{}.csv'.format(language, criterion)
    if not os.path.isfile(data_file):
        raise Exception('criterion {} of language {} does not exist'.format(criterion, language))


def load(language, criterion):
    data_file = 'data/criteria/{}/{}.csv'.format(language, criterion)
    return pd.read_csv(data_file, sep='\t')
