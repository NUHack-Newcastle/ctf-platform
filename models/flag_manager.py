from models.event import Event


class FlagManager:
    def __init__(self, event: Event):
        self.__event: Event = event
