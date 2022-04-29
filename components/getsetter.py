class GetSetTer:
    def __init__(self):
        self.__val = None

    @property
    def val(self):
        return self.__val

    @val.setter
    def val(self, value):
        self.__val = value

    @val.deleter
    def val(self):
        del self.__val
