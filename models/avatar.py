import dicebear
from dicebear import DOptions


class Avatar(dicebear.DAvatar):

    def __init__(self, style: str, seed: str, options: dict):
        stock_options = dict((k, v) for k, v in options.items() if k in dicebear.models.default_options)
        custom_options = dict((k, v) for k, v in options.items() if k not in dicebear.models.default_options)
        super().__init__(style, seed, options=DOptions(**options), custom=custom_options)

    def __str__(self):
        return self.url_svg
