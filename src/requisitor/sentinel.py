# -*- coding: utf-8 -*-
# Copyright 2020 Matt Martz


class _Sentinel:
    def __bool__(self):
        return False

    __nonzero__ = __bool__


Sentinel = _Sentinel()
