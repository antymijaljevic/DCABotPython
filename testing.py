# Traceback (most recent call last):
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\connection.py", line 169, in _new_conn
#     conn = connection.create_connection(
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\util\connection.py", line 73, in create_connection    for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\socket.py", line 954, in getaddrinfo
#     for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
# socket.gaierror: [Errno 11001] getaddrinfo failed

# During handling of the above exception, another exception occurred:

# Traceback (most recent call last):
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\connectionpool.py", line 699, in urlopen
#     httplib_response = self._make_request(
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\connectionpool.py", line 382, in _make_request
#     self._validate_conn(conn)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\connectionpool.py", line 1010, in _validate_conn
#     conn.connect()
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\connection.py", line 353, in connect
#     conn = self._new_conn()
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\connection.py", line 181, in _new_conn
#     raise NewConnectionError(
# urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPSConnection object at 0x000001606B9C7C10>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed

# During handling of the above exception, another exception occurred:

# Traceback (most recent call last):
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\requests\adapters.py", line 439, in send
#     resp = conn.urlopen(
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\connectionpool.py", line 755, in urlopen
#     retries = retries.increment(
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\urllib3\util\retry.py", line 574, in increment
#     raise MaxRetryError(_pool, url, error or ResponseError(cause))
# urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='api.binance.com', port=443): Max retries exceeded with url: /api/v3/ping (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x000001606B9C7C10>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed'))

# During handling of the above exception, another exception occurred:

# Traceback (most recent call last):
#   File "c:\Users\antym\Desktop\binance_bot\bot-run.py", line 300, in <module>
#     bot.spotWalletBalance()
#   File "c:\Users\antym\Desktop\binance_bot\bot-run.py", line 248, in spotWalletBalance
#     spotWallet = self.apiCall(lambda: self.client.get_account())
#   File "c:\Users\antym\Desktop\binance_bot\bot-run.py", line 62, in apiCall
#     self.client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, {"timeout": 2}) #, testnet=True
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\binance\client.py", line 300, in __init__
#     self.ping()
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\binance\client.py", line 526, in ping
#     return self._get('ping', version=self.PRIVATE_API_VERSION)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\binance\client.py", line 371, in _get
#     return self._request_api('get', path, signed, version, **kwargs)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\binance\client.py", line 334, in _request_api
#     return self._request(method, uri, signed, **kwargs)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\binance\client.py", line 314, in _request
#     self.response = getattr(self.session, method)(uri, **kwargs)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\requests\sessions.py", line 555, in get
#     return self.request('GET', url, **kwargs)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\requests\sessions.py", line 542, in request
#     resp = self.send(prep, **send_kwargs)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\requests\sessions.py", line 655, in send
#     r = adapter.send(request, **kwargs)
#   File "C:\Users\antym\AppData\Local\Programs\Python\Python39\lib\site-packages\requests\adapters.py", line 516, in send
#     raise ConnectionError(e, request=request)
# requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.binance.com', port=443): Max retries exceeded with url: /api/v3/ping (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x000001606B9C7C10>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed'))
# PS C:\Users\antym\Desktop\binance_bot>

import urllib.request

def internet_on():
    try:
        urllib.request.urlopen('http://www.google.com', timeout=2)
        return True
    except:
        return False


print(internet_on())