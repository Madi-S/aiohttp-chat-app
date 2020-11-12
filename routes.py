from handlers.chat import *
from handlers.login import *


routes = [('GET', '/login', signIn),
          ('POST', '/login', login),
          ('GET', '/chat', chat),
          ('POST', '/chat', send_chat),
          ('*', '/{tail:.*}', handle_get)]


def setup_routes(app):
    for route in routes:
        app.router.add_route(*route)
