import requests

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