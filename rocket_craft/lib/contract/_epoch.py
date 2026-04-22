class _Epoch:
    _value: int
    _transition: bool

    def __incr(self) -> "_Epoch":
        e = _Epoch("0")
        e._value = self._value + 1
        e._transition = True
        return e

    def __init__(self, epoch: str):
        if epoch.endswith("*"):
            self._value = int(epoch[:-1])
            self._transition = True
        else:
            self._value = int(epoch)
            self._transition = False

    def __str__(self) -> str:
        return f"{self._value}{'*' if self._transition else ''}"

    def __repr__(self) -> str:
        return f"_Epoch({self._value}{'*' if self._transition else ''})"

    def __add__(self, other: 1) -> "_Epoch":
        if other != 1:
            raise ValueError("Epoch can only be incremented by 1")

        return self.__incr()


def get_next_epoch(current: str) -> _Epoch:
    return _Epoch(current) + 1
