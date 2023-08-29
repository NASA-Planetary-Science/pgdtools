"""Ensure that no configuration file returns a 404 error.

This test only checks if a `404` error is encountered. If the computer running the tests
is offline, this test will pass. However, if the computer is online, this test will
fail if the configuration files are not found.
We depend here on the CI to ensure that the configuration files are always available.
"""

import pytest
import requests

from pgdtools import data


ALL_URLS = [data.BIBFILE, data.DB_JSON, data.REFERENCES_JSON, data.TECHNIQUES_JSON]


@pytest.mark.parametrize("url", ALL_URLS)
def test_urls(url):
    """Ensure that no URL when requested returns a 404 error."""
    with requests.get(url, stream=True) as rin:
        assert rin.status_code != 404
