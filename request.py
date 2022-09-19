import grequests, requests

class quickrequest:
    list = []
    list_map = []
    def __init__(self, listIps, url, key, files=None, json=None):
        self.list = []
        for i, item in enumerate(listIps, 1):
            self.list.append((url.replace("$ip", f"{item[0]}"), {"Authorization": f'Bearer {key}'}, files, json, item[0]))

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
        self.list_map = grequests.map(rs)

    def handler_requests(self, mess_ex, req_mess_ex):
        _string = ""
        req_list = self.list_map

        for i, item in enumerate(self.list, 1):
            server_message = "SERVER OFFLINE" if not req_list[i-1] else \
                req_mess_ex.format(response_message = req_list[i-1].json()['msg'])
            _string += mess_ex.format(i = i, serverIP = item[4], server_message=server_message)

        return [_string[x:x+4096] for x in range(0, len(_string), 4096)]

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