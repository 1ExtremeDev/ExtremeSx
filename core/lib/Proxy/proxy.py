class Proxy:
    def __init__(self, proxy: dict=None) -> None:
        if proxy is not None and len(proxy) == 2: self.proxy = proxy  
        else: self.proxy = None
        self.format()
    def format(self):
        if self.proxy is None: self.action = self.proxy
        else:  
            if self.proxy[0] not in ['http', 'socks4', 'socks5']: self.action = None
            else: 
                if self.proxy[0] == ['http', 'socks4', 'socks5'][0]:
                    self.action = dict(
                        http = "https://%s" % (self.proxy[1]),
                        https = "https://%s" % (self.proxy[1])
                    )
                elif self.proxy[0] == ['http', 'socks4', 'socks5'][1]:
                    self.action = dict(
                        http = "socks4://%s" % (self.proxy[1]),
                        https = "socks4://%s" % (self.proxy[1])
                    )
                elif self.proxy[0] == ['http', 'socks4', 'socks5'][2]:
                    self.action = dict(
                        http = "socks5://%s" % (self.proxy[1]),
                        https = "socks5://%s" % (self.proxy[1])
                    )

class Check:
    def __init__(self, 
        proxy: str = None) -> None:
        if proxy is None:
            self._return = None
        else:
            self.\
                proxy = proxy
            self._return = self.check()
    
    def check(self):
        from proxy_checking import (
            ProxyChecker
        )
        try: return ProxyChecker().check_proxy(self.proxy)
        except: return False
