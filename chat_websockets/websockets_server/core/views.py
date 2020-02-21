from aiohttp import web, WSMsgType, WSCloseCode
from utils.log_helper import setup_logger
import traceback

logger = setup_logger(__name__)


class WebSocketView(web.View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = self.request.app

    async def get(self):

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        ws_id = self.app.extract_websockets_id(self.request, ws)
        logger.info("received connection from : %s", ws_id)
        await self.app.handle_ws_connect(ws_id, ws)

        async for msg_raw in ws:
            if msg_raw.type == WSMsgType.TEXT:
                try:
                    await self.app.process_msg_outbound(msg_raw.data, ws_id)
                except (ValueError, Exception) as e:
                    logger.error('[%s] generic error. Exception: %s', ws_id, e)
                    logger.error('\n%s', traceback.format_exc())
                    await ws.close(code=WSCloseCode.UNSUPPORTED_DATA, message=str(e))
                    break

            elif msg_raw.type == WSMsgType.ERROR:
                logger.warn('[%s] ws connection: closed with exception %s', ws_id, ws.exception())
        logger.info('[%s] websocket connection closed', ws_id)
        await self.app.handle_ws_disconnect(ws_id)
        return ws
