#!/usr/bin/python3

from abc import ABCMeta, abstractmethod


class WebEngine(metaclass=ABCMeta):
    def __init__(self, engine_name):
        self.name = engine_name

    # @abstractmethod
    def check(self, engine_path):
        pass
