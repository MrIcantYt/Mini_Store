from hashlib import sha256
from hmac import compare_digest, new
from json import dumps, loads
from os import PathLike, fsync, path, replace
from pathlib import Path
from typing import Any, Final

from mini_store.exceptions import SignCheckError

SECRET: Final[bytes] = ('o@k!' + '9dNz' + 'H#SC' + 'vb4d' + '!3y*').encode()


class SignedJson:
    def __init__(
        self, file_path: str | PathLike[str], *, secret: bytes = SECRET, check_sign: bool = True
    ) -> None:
        self.file_path = Path(file_path)
        self.secret = secret
        self._need_check_sign = check_sign

    def _get_save_sign(self, json_str: str) -> str:
        return new(self.secret, json_str.encode(), sha256).hexdigest()

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
        tmp_file = self.file_path.with_name(f'{self.file_path.name}.tmp')  # game.json.tmp

        try:
            with open(tmp_file, 'w') as f:
                f.write(signed_save)
                # lines below needed to maintain atomicity
                f.flush()  # Python-buffer -> kernel
                fsync(f.fileno())  # kernel -> disk

            replace(tmp_file, self.file_path)
        finally:
            if tmp_file.exists():
                tmp_file.unlink()

    def load(self, *, verify_sign: bool = True) -> dict[str, Any]:
        if not path.exists(self.file_path):
            raise FileNotFoundError()

        with open(self.file_path, 'r') as f:
            signed_save = f.read().strip()

        if not signed_save:
            return {}

        sign, save = self._split_sign_and_save(signed_save)

        if (verify_sign and self._need_check_sign) and not self._sign_check(sign, save):
            raise SignCheckError()

        return loads(save)
