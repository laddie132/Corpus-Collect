# -*- coding: utf-8 -*-

__author__ = 'Han'

import sys
import yaml
import json
import random
import logging
import logging.config


def init_logging(config_path='config/logging_config.yaml'):
    """
    initial logging module with config
    :param config_path:
    :return:
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    except IOError:
        sys.stderr.write('logging config file "%s" not found' % config_path)
        logging.basicConfig(level=logging.DEBUG)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Dataset(metaclass=Singleton):
    def __init__(self, json_path, start_idx=100):
        self.start_idx = start_idx

        with open(json_path, 'r') as f:
            self.data = json.load(f)

    def random_select(self):
        return random.choice(self.data)

    def select(self):
        rtn_data = self.data[self.start_idx]
        self.start_idx = (self.start_idx + 1) % len(self.data)

        return rtn_data

    def get_idx(self):
        return self.start_idx
