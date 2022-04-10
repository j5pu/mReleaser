# coding=utf-8
"""
Start
"""

from mreleaser import cli_invoke
from mreleaser import app


def test_help():
    """
    cli --help
    """
    result = cli_invoke(app, ["--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")
