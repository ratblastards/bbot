# -*- coding: utf-8 -*-

# Python 3

import requests
import os
from requests.compat import urljoin


DISCORD_ALERT = os.getenv("DISCORD_ALERT_WEBHOOK")
DISCORD_ADMIN = os.getenv("DISCORD_ADMIN_WEBHOOK")

# temp
if DISCORD_ADMIN is None:
    DISCORD_ADMIN = DISCORD_ALERT

def send(webhook, message = None, title = None, description = None):

    data =  {
		"content" : message
	}
	
    embed = None
	
    if title and description:
		
        embed = {
			"description" : description,
			"title" : title			
        }

    else:
        if title:
            embed = {
                "title" : title			
            }			
        if description:
            embed = {
			    "description" : description,
            }

    if embed:
        data["embeds"] = [embed]

    result = requests.post(webhook, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered  OK, code {}.".format(result.status_code))
