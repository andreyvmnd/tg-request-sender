import requests
import config

class request:
    error = "other"
    def __init__(self, key, url, files={}, json={}):
        try:
            c = requests.Session()
            response = c.post(
                    headers={"Authorization": f'Bearer {key}'},
                    url=url,
                    allow_redirects=False
                )
            self.response = response
        except Exception as e:
            self.error = f"Exception: {e}\n"
            
        return self


if __name__ == "__main__":
    self_req = request(config.ACCESS_TOKEN, f"http://localhost:5000/bots/isonline")
    print(self_req.error)
    print(self_req.response)
