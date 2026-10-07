from hashlib import sha256
from hmac import compare_digest, new
from json import dumps, loads
from os import path
from typing import Final

from mini_store.exceptions import SignCheckError

SECRET: Final[bytes] = ('o@k!' + '9dNz' + 'H#SC' + 'vb4d' + '!3y*').encode()


class SignedJson:
    def __init__(self, file_path: str, secret: bytes = SECRET) -> None:
        self.file_path = file_path
        self.secret = secret

    def _sign(self, json_str: str) -> str:
        return new(self.secret, json_str.encode('utf-8'), sha256).hexdigest()

    def _sign_check_and_get_save(self, signed_save: str) -> str:
        if '\n' not in signed_save:
            raise ValueError('Файл повреждён')
        sign, save = signed_save.split('\n', 1)
        expected_sign = self._sign(save)
        if not compare_digest(sign, expected_sign):
            raise SignCheckError()
        return save

    def dump(self, save: dict) -> None:
        json_save = dumps(save, separators=(',', ':'), ensure_ascii=False)
        signed_save = self._sign(json_save) + '\n' + json_save
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(signed_save)

    def load(self, check_sign: bool = True) -> dict:
        if not path.exists(self.file_path):
            return {}

        with open(self.file_path, 'r', encoding='utf-8') as f:
            signed_save = f.read()

        if not signed_save.strip():
            return {}

        if check_sign:
            save = self._sign_check_and_get_save(signed_save)
        else:
            _, save = signed_save.split('\n', 1)

        return loads(save)
