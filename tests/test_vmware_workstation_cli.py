#!/usr/bin/env python

"""Tests for `vmware_workstation_cli` package."""

import pytest
from click.testing import CliRunner

from vmware_workstation_cli import __version__, cli, vmware_workstation_cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_version():
    """Test reading version and module name"""
    assert (
        vmware_workstation_cli.__name__
        == "vmware_workstation_cli.vmware_workstation_cli"
    )
    assert __version__
    assert isinstance(__version__, str)


def test_cli():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0, result
    assert "Show this message and exit." in result.output, result
