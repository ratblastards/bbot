# -*- coding: utf-8 -*-

# Python 3

import os
import bbot.airtable
import bbot.raidhelper
import bbot.discord
import bbot.healthcheck

def env_secret(secret_name : str) -> str:

    return os.getenv(secret_name)