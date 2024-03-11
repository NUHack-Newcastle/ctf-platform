from abc import ABC, abstractmethod


class Icon(ABC):

    @abstractmethod
    def __str__(self):
        raise NotImplemented
