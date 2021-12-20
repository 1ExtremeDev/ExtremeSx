from requests.models import Response
from core.lib.Proxy.proxy import Proxy


class privateSpam:
    """
    This class sends a private discord message
    """
    def __init__(self,
        token: str,
        message: str,
        identifier: str,
        proxy: list = None
    ) -> None:
        self.proxy = proxy if proxy is not None else None
        self.message = message if message is not None else "ExtremeDev Spammer"
        self.id = identifier
        self.token = token
        self.send()

    def send(self):
        import requests, json
        from randstr import (
            randstr
        )

        headers = {"Authorization": self.token,
                   "accept": "*/*",
                   "accept-language": "en-GB",
                   "content-length": "90",
                   "content-type": "application/json",
                   "cookie": f"__cfuid={randstr(43)}; __dcfduid={randstr(32)}; locale=en-US",
                   "origin": "https://discord.com",
                   "sec-fetch-dest": "empty",
                   "sec-fetch-mode": "cors",
                   "sec-fetch-site": "same-origin",
                   "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36",
                   "x-debug-options": "bugReporterEnabled",
                   "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAzIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI0NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6InNrIiwiY2xpZW50X2J1aWxkX251bWJlciI6OTkwMTYsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
        }
        requestResponse = requests.post(
            "https://discordapp.com/api/v9/users/@me/channels",
            headers = headers,
            json = {
                'recipient_id': self.id
            },
            proxies = Proxy(self.proxy) if type(self.proxy) is list else None
        )
        responseJson = json.loads(requestResponse.content)
        requestFinal = requests.post(
            "https://discordapp.com/api/v9/channels/{}/messages".format(responseJson['id']),
            headers = headers,
            json =  {
                "content": self.message, 
                "tts": False
            },
            proxies = Proxy(self.proxy) if type(self.proxy) is list else None
        )
        if requestFinal.status_code == 429:
            ratelimit = str(float(json.loads(requestFinal.content)['retry_after']))
            self.r, self.ratelimit = 'ratelimit', ratelimit
        elif requestFinal.status_code == 200:
            self.r = 'sent'
        elif 'You need to verify your account in order to perform this action.' in requestFinal.text:
            self.r = 'unverified'
        elif 'Access denied' in requestFinal.text:
            self.r = 'denied'
        elif 'Unauthorized' in requestFinal.text:
            self.r = 'invalid'
        else:
            self.r = 'other'

        
class serverSpam:
    """
    This class sends a message to a channel id on discord
    """
    def __init__(self,
        token: str,
        message: str,
        identifier: str,
        proxy: list = None
    ) -> None:
        self.proxy = proxy if proxy is not None else None
        self.message = message if message is not None else "ExtremeDev Spammer"
        self.id = identifier
        self.token = token
        self.send()

    def send(self):
        import requests, json
        requestResponse = requests.post(
            "https://discordapp.com/api/channels/{}/messages".format(
                str(self.id)
            ),
            headers = {"Authorization": self.token, 
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
                       "Content-Type": "application/json"
            },
            json = {
                "content": self.message
            },
            proxies = Proxy(self.proxy) if type(self.proxy) is list else None
        )
        if requestResponse.status_code == 429:
            ratelimit = str(float(json.loads(requestResponse.content)['retry_after']))
            self.r, self.ratelimit = 'ratelimit', ratelimit
        elif requestResponse.status_code == 200:
            self.r = 'sent'
        elif 'You need to verify your account in order to perform this action.' in requestResponse.text:
            self.r = 'unverified'
        elif 'Access denied' in requestResponse.text:
            self.r = 'denied'
        elif 'Unauthorized' in requestResponse.text:
            self.r = 'invalid'
        else:
            self.r = 'other'

class friendRequest:
    """
    This class adds an account by its username and discriminator (discriminator must be 4 letters long)
    """
    def __init__(self,
        token: str,
        username: str,
        discriminator: str,
        proxy: list = None
    ) -> None:
        self.proxy = proxy if proxy is not None else None
        self.discriminator = discriminator if len(discriminator) == 4 else discriminator
        self.username = username
        self.token = token
        self.request()

    def request(self):
        import requests, json

        requestResponse = requests.post(
            "https://discordapp.com/api/v6/users/@me/relationships",
            headers = {
                "Authorization": self.token, 
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", 
                "Content-Type":"application/json"
            },
            json = {
                "username": self.username, 
                "discriminator": self.discriminator
            },
            proxies = Proxy(self.proxy) if type(self.proxy) is list else None
        )
        if 'You need to verify your account in order to perform this action.' in requestResponse.text:
            self.r = 'unverified'
        elif 'Unauthorized' in requestResponse.text:
            self.r = 'invalid'
        elif 'Access denied' in requestResponse.text:
            self.r = 'denied'
        elif 'Unknown' in requestResponse.text:
            self.r = 'unknown'
        else:
            self.r = 'sent'

class Report:
    """
    This class reports someone account
    """
    def __init__(self,
        token: str,
        messageID: str,
        channelID: str,
        guildID: str,
        reason: str = None,
        proxy: list = None
    ) -> None:
        self.proxy = proxy if proxy is not None else None
        self.messageID = messageID
        self.channelID = channelID
        self.guildID = guildID
        self.reason = reason if reason is not None else "THINGY"
        self.token = token
        self.send()

    def send(self):
        import requests, json

        requestResponse = requests.post(
            "https://discord.com/api/v9/report",
            headers = {
                'Authorization': self.token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36',
                'Content-Type': 'application/json'
            },
            json = {
                "channel_id": self.channelID, 
                "guild_id": self.guildID, 
                "message_id": self.messageID, 
                "reason": self.reason
            },
            proxies = Proxy(self.proxy) if type(self.proxy) is list else None
        )
        if requestResponse.status_code == 201:
            self.r = 'sent'
        elif requestResponse.status_code == 401:
            self.r = 'invalid'
        else:
            self.r = 'other'