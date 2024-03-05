import bcrypt


class Password:

    def __init__(self):
        self.__hash: str = ''

    def __eq__(self, other: str):
        if not isinstance(other, str):
            return NotImplemented

        return bcrypt.checkpw(other.encode('utf-8'), self.__hash.encode('utf-8'))

    @property
    def hash(self) -> str:
        return self.__hash

    @staticmethod
    def from_hash(hash: str) -> 'Password':
        p = Password()
        p.__hash = hash
        return p

    @staticmethod
    def from_plaintext(plaintext: str) -> 'Password':
        p = Password()
        p.__hash = bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return p
