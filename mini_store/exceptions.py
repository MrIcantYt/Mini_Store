class SignCheckError(Exception):
    def __init__(
        self, message: str = 'Файл сохранения повреждён (подпись не совпала)'
    ) -> None:
        self.message = message
        super().__init__(message)
