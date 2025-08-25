import os
import sys

import pytest

from . import something


def my_func():
    print(os.getcwd())
    print(sys.version)
    assert something
    assert pytest
