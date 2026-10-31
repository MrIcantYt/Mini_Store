import pytest

from mini_store.exceptions import SignCheckError
from mini_store.sign import SignedJson

SECRET = b'test-secret'


class TestSignedJson:
    def test_dump_and_load(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        save = {'players': [{'id': 1, 'name': 'Тест'}], 'version': 1}
        signed = SignedJson(str(path), secret=SECRET)

        signed.dump(save)

        assert signed.load() == save

    def test_file_contains_signature_and_json(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        signed = SignedJson(str(path), secret=SECRET)

        signed.dump({'a': 1})

        content = path.read_text(encoding='utf-8')
        sign, save = content.split('\n', 1)
        assert len(sign) == 64
        assert save == '{"a":1}'

    def test_missing_file(self, tmp_path) -> None:
        signed = SignedJson(str(tmp_path / 'missing.json'), secret=SECRET)

        with pytest.raises(FileNotFoundError):
            signed.load()

    def test_empty_file_returns_empty_dict(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        path.write_text('', encoding='utf-8')

        assert SignedJson(str(path), secret=SECRET).load() == {}

    def test_file_without_separator(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        path.write_text('broken', encoding='utf-8')

        with pytest.raises(ValueError, match='Файл повреждён'):
            SignedJson(str(path), secret=SECRET).load()

    def test_tampered_file(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        signed = SignedJson(str(path), secret=SECRET)
        signed.dump({'a': 1})

        path.write_text('bad-sign\n{"a":2}', encoding='utf-8')

        with pytest.raises(SignCheckError):
            signed.load()

    def test_tampered_file_without_check(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        signed = SignedJson(str(path), secret=SECRET)
        signed.dump({'a': 1})
        path.write_text('bad-sign\n{"a":2}', encoding='utf-8')

        unchecked = SignedJson(str(path), secret=SECRET, check_sign=False)

        assert unchecked.load() == {'a': 2}

    def test_force_check_false_skips_signature(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        signed = SignedJson(str(path), secret=SECRET)
        signed.dump({'a': 1})
        path.write_text('bad-sign\n{"a":2}', encoding='utf-8')

        assert signed.load(force_check=False) == {'a': 2}

    def test_different_secret_produces_different_sign(self, tmp_path) -> None:
        path = tmp_path / 'save.json'
        SignedJson(str(path), secret=b'one').dump({'a': 1})
        first = path.read_text(encoding='utf-8')

        SignedJson(str(path), secret=b'two').dump({'a': 1})
        second = path.read_text(encoding='utf-8')

        assert first != second
