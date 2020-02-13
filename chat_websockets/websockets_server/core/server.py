from aiohttp import web
from websockets_server.core import views


app = web.Application()
app.router.add_get('/ws', views.WebSocketView)
