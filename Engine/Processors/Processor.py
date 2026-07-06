from abc import ABC, abstractmethod


class Processor(ABC):

    def __init__(self, name=None):

        self.name = name or self.__class__.__name__

    @abstractmethod
    def process(self, document):

        raise NotImplementedError
