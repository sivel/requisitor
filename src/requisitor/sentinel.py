class _Sentinel:
    def __bool__(self):
        return False

    __nonzero__ = __bool__


Sentinel = _Sentinel()
