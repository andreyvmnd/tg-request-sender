import requests

class request:
    error = None
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
            self.response = response
        except Exception as e:
            self.error = f"Exception: {e}"