# -*- coding: utf-8 -*-

from manager import Manager
from settings import settings

manager = Manager()
if settings.ACTION == 'comparator':
    manager.compare()
elif settings.ACTION == 'parametor':
    manager.score_parameters()
else:
    raise Exception('Unknown action : \'{}\''.format(settings.ACTION))
