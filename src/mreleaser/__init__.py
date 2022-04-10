# coding=utf-8
"""
Mreleaser __init__.py Module
"""
__all__ = (
    "ExcType",
    "suppress",
    "version",
)

import contextlib
import importlib.metadata

from pathlib import Path
from typing import Callable
from typing import ParamSpec
from typing import Type
from typing import TypeAlias
from typing import TypeVar

ExcType: TypeAlias = Type[Exception] | tuple[Type[Exception], ...]
PROJECT: str = Path(__file__).parent.name
T = TypeVar('T')
P = ParamSpec('P')


def suppress(func: Callable[P, T], *args: P.args, exception: ExcType | None = Exception, **kwargs: P.kwargs) -> T:
    """
    Try and supress exception.

    """
    with contextlib.suppress(exception or Exception):
        return func(*args, **kwargs)


def version(package: str = PROJECT) -> str:
    """
    Package installed version

    Examples:
        >>> from semver import VersionInfo
        >>> assert VersionInfo.parse(version("pip"))

    Arguments:
        package: package name (Default: `PROJECT`)

    Returns
        Installed version
    """
    return suppress(importlib.metadata.version, package or Path(__file__).parent.name,
                    exception=importlib.metadata.PackageNotFoundError)
