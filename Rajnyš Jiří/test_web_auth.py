import http.client, urllib.parse, time
from potapec.database.database import get_user

HOST='127.0.0.1'
PORT=5000

def post(path, params, cookie=None):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    body = urllib.parse.urlencode(params)
    hdrs = {'Content-Type':'application/x-www-form-urlencoded'}
    if cookie: hdrs['Cookie']=cookie
    conn.request('POST', path, body, hdrs)
    r = conn.getresponse()
    data = r.read().decode(errors='ignore')
    set_cookie = r.getheader('Set-Cookie')
    return r.status, set_cookie, data

for i in range(20):
    try:
        conn = http.client.HTTPConnection(HOST, PORT, timeout=1)
        conn.request('GET', '/')
        r = conn.getresponse()
        r.read()
        break
    except Exception:
        time.sleep(0.5)
else:
    print('Server not reachable')
    raise SystemExit(1)

username='ci_test_user'
password='ci_test_pass'
status, set_cookie, body = post('/signup', {'username':username, 'password':password})
print('POST /signup ->', status)
print('Set-Cookie:', set_cookie)
row = get_user(username)
print('DB row:', row)

status, set_cookie_login, body = post('/login', {'username':username, 'password':password})
print('POST /login ->', status)
print('Set-Cookie (login):', set_cookie_login)
cookie = None
if set_cookie_login:
    cookie = set_cookie_login.split(';',1)[0]
elif set_cookie:
    cookie = set_cookie.split(';',1)[0]
if cookie:
    import http.client
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    conn.request('GET', '/', headers={'Cookie': cookie})
    r = conn.getresponse()
    page = r.read().decode(errors='ignore')
    print('GET / (logged in?) length=', len(page))
    print('\n'.join(page.splitlines()[:20]))
else:
    print('No cookie found; cannot verify session')
