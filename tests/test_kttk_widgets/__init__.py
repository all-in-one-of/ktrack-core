import os

import pytest


def has_pyside_no_maya():
    # type: () -> bool
    """
    Checks if PySioe or PySide2 is avaible
    :return: True if avaible, False otherwise
    """
    try:
        import maya.cmds as cmds
        return False
    except:
        pass
    try:
        import PySide
        return True
    except:
        pass
    try:
        import PySide2
        return True
    except:
        pass
    return False


pyside_only = pytest.mark.skipif(not has_pyside_no_maya(), reason="requires PySide")