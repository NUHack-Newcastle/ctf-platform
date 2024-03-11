from models.icon import Icon


class IconBootstrap(Icon):
    def __init__(self, icon_name: str):
        super().__init__()
        self.__icon_name = icon_name

    def __str__(self):
        return f"<i class=\"bi bi-{self.__icon_name}\"></i>"