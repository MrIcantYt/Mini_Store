from hashlib import sha256
from hmac import compare_digest, new
from json import dumps, loads
from os import path
from typing import Any, Final

from mini_store.exceptions import SignCheckError

SECRET: Final[bytes] = ('o@k!' + '9dNz' + 'H#SC' + 'vb4d' + '!3y*').encode()


class SignedJson:
    def __init__(
        self, file_path: str, *, secret: bytes = SECRET, check_sign: bool = True
    ) -> None:
        self.file_path = file_path
        self.secret = secret
        self._need_check_sign = check_sign

    def _get_save_sign(self, json_str: str) -> str:
        """Return sha256 with salt sign for save."""
        return new(self.secret, json_str.encode('utf-8'), sha256).hexdigest()

    def _sign_check(self, sign: str, save: str) -> bool:
        expected_sign = self._get_save_sign(save)
        return compare_digest(sign, expected_sign)

    def _split_sign_and_save(self, signed_save: str) -> list[str]:
        if '\n' not in signed_save:
            raise ValueError('Файл повреждён')
        return signed_save.split('\n', 1)

    def dump(self, save: dict) -> None:
        json_save = dumps(save, separators=(',', ':'), ensure_ascii=False)
        signed_save = self._get_save_sign(json_save) + '\n' + json_save
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(signed_save)

    def load(self, force_check: bool = True) -> dict[str, Any]:
        """Load save from file with checking sign if `self._check_sign` and `force_check`"""
        if not path.exists(self.file_path):
            raise FileNotFoundError()

        with open(self.file_path, 'r', encoding='utf-8') as f:
            signed_save = f.read().strip()

        if not signed_save:
            return {}

        sign, save = self._split_sign_and_save(signed_save)

        need_check = self._need_check_sign and force_check
        if need_check and not self._sign_check(sign, save):
            raise SignCheckError()
        return loads(save)
