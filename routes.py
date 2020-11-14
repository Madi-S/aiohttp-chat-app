from handlers.chat import *
from handlers.login import *


routes = [('GET', '/login', get_login),
          ('POST', '/login', post_login),
          ('GET', '/logout', get_logout),
          ('POST', '/logout', post_logout),
          ('GET', '/register', get_register),
          ('GET', '/chat', get_chat),
          ('POST', '/send', post_send),
          ('POST', '/recover', post_recover),
          ('*', '/{tail:.*}', handle_all)]


def setup_routes(app):
    for route in routes:
        app.router.add_route(*route)
