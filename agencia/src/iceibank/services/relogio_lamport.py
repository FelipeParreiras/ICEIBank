from threading import Lock


class LamportClock:
    def __init__(self) -> None:
        self._value = 0
        self._lock = Lock()

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

    def ao_enviar(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    def ao_receber(self, recebido: int) -> int:
        with self._lock:
            self._value = max(self._value, recebido) + 1
            return self._value
