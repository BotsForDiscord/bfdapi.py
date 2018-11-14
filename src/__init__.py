# -*- coding: utf-8 -*-

"""
Bots For Discord API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Python wrapper for the Bots For Discord API

"""

__title__ = 'bfd.py'
__author__ = 'JackTEK'
__license__ = 'AGPL-3.0'
__copyright__ = 'Copyright 2018 Bots for Discord'
__version__ = '1.0.0'

from collections import namedtuple
import requests
from datetime import datetime
import asyncio
import requests

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=1, minor=0, micro=0, releaselevel='stable', serial=0)

class LoginError(Exception):
    pass

class ClientError(Exception):
    pass

def Route(endpoint, method, data={}, token=None):
    base = "https://botsfordiscord.com/api/"

    headers = {}
    if token or data != {}:
        if isinstance(data, dict):
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = token

    url = f"{base}{endpoint}"
    return requests.request(method.upper(), url, json=data, headers=headers)

class Client:
    def __init__(self, bot, token):
        self.token = token
        self.bot = bot

    async def loop_server_count(self, time: int):
        if time < 300:
            raise ClientError("To avoid ratelimits, the post interval must be above or equal to 5 mins (300 secs)!")
        while True:
            req = Route(f"bot/{self.bot.user.id}", "POST", data={"server_count": len(self.bot.guilds)}, token=self.token)
            if req.status_code == 400:
                raise ClientError("The API rejected the parsed token, the request loop has been broken!")
            await asyncio.sleep(time)

    def get_bot(self, bot_id: int):
        req = Route(f"bot/{bot_id}", "GET")
        if req.status_code == 404:
            raise ClientError("Bot not found!")
        if req.status_code != 200:
            raise ClientError(f"API a {req.status_code} status code!")
        return Bot(req.json(), bot=self.bot)

class Bot():
    def __init__(self, data: dict, bot=None):
        self.approved = data["approved"]
        self.avatar = data["avatar"]
        self.bot = bot
        self.client_id = data["clientId"]
        self.id = data["id"]
        self.color = data["color"]
        self.colour = self.color
        self.discrim = data["discrim"]
        self.featured = data["featured"]
        self.github = data["github"]
        self.invite = data["invite"]
        self.library = data["library"]
        self.name = data["name"]
        self.owner = data["owner"]
        self.owner_ids = data["owners"].append(data["owner"]) if data["owners"] != [] else data["owner"]
        self.prefix = data["prefix"]
        self.server_count = data["server_count"]
        self.short_desc = data["short_desc"]
        self.support_server = data["support_server"]
        self.tag = data["tag"]
        self.vanity_url = data["vanityUrl"]
        self.verified = data["verified"]
        self.votes = data["votes"]
        self.votes_today = data["votes24"]
        self.votes_month = data["votesMonth"]
        self.webpage = f"https://botsfordiscord.com/bots/{self.id if self.vanity_url == '' else self.vanity_url}"
        self.website_bot = data["website_bot"]
        self.widget = f"https://botsfordiscord.com/api/bot/{self.id}/widget"

    def __str__(self):
        return self.tag

    @property
    def links(self):
        links = [self.invite, self.webpage, self.widget]
        if self.github != "":
            links.append(self.github)
        if self.support_server != "":
            links.append(self.support_server)
        return links

    def get_widget(self, theme: str=None, width: int=None):
        base = f"https://botsfordiscord.com/api/bot/{self.id}/widget"
        if theme == "dark":
            base = base + "?theme=dark"
        if width:
            base = base + f"?width={width}"
        return base

    @property
    def devs(self):
        owners = []
        if len(self.owner_ids) > 0:
            for x in self.owner_ids:
                owners.append(Dev(x, bot=self.bot))
        else:
            owners.append(Dev(self.owner, bot=self.bot))
        return owners

class Dev():
    def __init__(self, id, bot=None):
        self.bot = bot
        data = requests.get(f"https://discordapp.com/api/v7/users/{id}", headers={"Authorization": f"Bot {self.bot.http.token}"}).json()
        self.user = f"{data['username']}#{data['discriminator']}"
        self.id = data['id']
        self.name = data["username"]
        self.discriminator = data["discriminator"]
        self.mention = f"<@{self.id}>"
        data = Route(f"user/{self.id}", "GET")
        self.background = data["background"]
        self.bio = data["bio"]
        self.admin = data["isAdmin"]
        self.mod = data["isMod"]
        self.verified = data["isVerifiedDev"]
        self.website = data["website"]

    def __str__(self):
        return self.user

    @property
    def bots(self):
        data = Route(f"user/{self.id}/bots", "GET")
        if data.status_code == 404:
            return []
        if data.status_code == 200:
            bots = []
            for x in data["bots"]:
                data = Route(f"bot/{x}", "GET")
                bots.append(Bot(data.json()))
            return bots
