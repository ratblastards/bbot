# -*- coding: utf-8 -*-

# Python 3

from __future__ import annotations
import requests
from requests.compat import urljoin
from datetime import datetime
from dateutil import tz

utc_zone = tz.gettz('UTC')
local_zone = tz.gettz('Europe/Berlin')

RAID_HELPER_URL="https://raid-helper.dev/api/v2/"

        # when is a javascript datetime string, like: 2023-04-29T19:00:00.000Z, based in UTC
        # RaidHelper expects local (Europe/Berlin) time as we've set that in a preference
        # So we use this function to convert it

def UTC_to_date_time(when_str):

    dt_UTC = datetime.fromisoformat(when_str.replace("Z","000")).replace(tzinfo=utc_zone)
    dt_local = dt_UTC.astimezone(local_zone)

    api_date = dt_local.strftime('%Y-%m-%d')
    api_time = dt_local.strftime('%H:%M')

    return api_date, api_time


class RaidHelper(object):

    def __init__(self, api_key, server, channel) -> RaidHelper:

        self.API_KEY=api_key
        self.SERVER=server
        self.CHANNEL=channel


    def header(self):

        return {
            'Authorization' : self.API_KEY, 
            'Content-Type' : 'application/json; charset=utf-8'
        }
    

    def delete(self, event_id):

        # https://raid-helper.dev/api/v2/events/EVENTID

        url = urljoin(RAID_HELPER_URL, f"events/{event_id}")

        header = self.header()

        result = requests.delete(url, headers = header)

        response = result.json()

        result = response.get("status", None)

        deleted = False

        if result == "Event deleted":
            deleted = True

        return deleted



    def update(self, event_id, leader, template, when, title, description=None):

        # https://raid-helper.dev/api/v2/events/EVENTID

        dateWhen, timeWhen = UTC_to_date_time(when)

        url = urljoin(RAID_HELPER_URL, f"events/{event_id}")

        header = self.header()

        data = {
            'leaderId' : leader,
            'templateId' : template,
            'date' : dateWhen,
            'time' : timeWhen,
            'title' : title
        }

        if description is not None:
            data['description'] = description

        result = requests.patch(url, headers = header, json=data)

        response = result.json()

        event = response.get("event", {})
        status = response.get("status", None)

        updated = False

        if status == "Event updated!":
            
            updated = True

        return(updated)


    def create(self, leader, template, when, title, description=None):

        dateWhen, timeWhen = UTC_to_date_time(when)

        url = urljoin(RAID_HELPER_URL,f"servers/{self.SERVER}/channels/{self.CHANNEL}/event")

        header = self.header()

        data = {
            'leaderId' : leader,
            'templateId' : template,
            'date' : dateWhen,
            'time' : timeWhen,
            'title' : title
        }

        if description is not None:
            data['description'] = description

        # We need the event ID
        result = requests.post(url, headers = header, json=data)

        response = result.json()

        event = response.get("event", {})
        status = response.get("status", None)
        event_id = None

        if status == "Event created!":
            
            event_id = event.get("id", None)
            print(f"Event successfully created with id {event_id}")

        return(event_id)

