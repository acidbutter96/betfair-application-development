import warnings

from pandas.core.common import SettingWithCopyWarning

from .core import *

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
