import grequests

def stringtolist(string):
    return [string[x:x+4096] for x in range(0, len(string), 4096)]

class quickrequest:
    list = []
    list_map = []
    def __init__(self, listIps, url, key, files=None, json=None):
        self.list = []
        for i, item in enumerate(listIps, 1):
            self.list.append([url.replace("$ip", f"{item[0]}"), {"Authorization": f'Bearer {key}'}, files, json, item[0]])

    def start(self, timeout=5):
        rs = (
            grequests.post(
                url=u[0], 
                headers=u[1], 
                files={'file': open(f"docs/{u[2]}", 'rb')} if u[2] else {}, 
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
            server_message = ""
            if req_list[i-1] == None:
                server_message = "SERVER OFFLINE"
            elif req_list[i-1].text and 'msg' in req_list[i-1].text:
                server_message = req_mess_ex.format(response_message = req_list[i-1].json()['msg'])
            else:
                server_message = req_mess_ex.format(response_message = req_list[i-1].ok)
            _string += mess_ex.format(i = i, serverIP = item[4], server_message=server_message)

        return stringtolist(_string)