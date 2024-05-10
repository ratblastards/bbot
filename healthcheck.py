# -*- coding: utf-8 -*-

# Python 3

import requests
import os
from requests.compat import urljoin

HEALTHCHECK_DOMAIN = "https://hc-ping.com/"
HEALTHCHECK_SECRET = os.getenv("HEALTHCHECK_SECRET")


def ping(slug):

    url = urljoin(urljoin(HEALTHCHECK_DOMAIN,f"{HEALTHCHECK_SECRET}/"), slug)
    requests.get(url)

