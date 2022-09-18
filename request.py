import grequests, requests

class quickrequest:
    list = []
    def __init__(self):
        self.list = []

    def addReq(self, url, key, files=None, json=None):
        sname = url[url.find("/") + 2 : url.find(":5")]
        self.list.append((url, {"Authorization": f'Bearer {key}'}, files, json, sname))

    def start(self, timeout=5):
        rs = (
            grequests.post(
                url=u[0], 
                headers=u[1], 
                files=u[2], 
                json=u[3], 
                allow_redirects=False,
                timeout=timeout
            ) for u in self.list
        )
        return grequests.map(rs)

class request:
    error = None
    isoffline = None
    def __init__(self, key, url, files=None, json=None):
        if files == None:
            files = {}
        if json == None:
            json = {}
            
        try:
            c = requests.Session()
            response = c.post(
                    headers={"Authorization": f'Bearer {key}'},
                    url=url,
                    files=files,
                    json=json,
                    allow_redirects=False
                )
            if response.ok:
                self.response = response
            else:
                self.error = response.json()
        except:
            self.isoffline = True