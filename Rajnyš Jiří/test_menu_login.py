from potapec.database.database import ensure_db, create_user, get_user
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'potapec'))
from werkzeug.security import generate_password_hash
from potapec.game.menu import Menu
import time

ensure_db()
username = f'menu_ci_user_{int(time.time())}'
password = 'menu_test_pass'

print('Existing?', get_user(username))

m = Menu(None, None)
m._auth_username = username
m._auth_password = password
ret = m._attempt_login()
print('Attempt signup result:', ret)
print('Menu.user:', m.user)
print('Auth message:', m._auth_message)

m2 = Menu(None, None)
m2._auth_username = username
m2._auth_password = password
ret2 = m2._attempt_login()
print('Attempt login result:', ret2)
print('Menu2.user:', m2.user)
print('Auth message 2:', m2._auth_message)

row = get_user(username)
print('DB row exists:', row is not None)
print('DB row:', row)
