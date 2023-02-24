from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
import json
from channels.db import database_sync_to_async
from acc.models import Chat
# global veriables
unknown_users = 0
ws_users = {}


class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('Websocket connected...', event)
        if self.scope["user"].is_authenticated:
            try:
                ws_users[self.scope["user"].id].append(self)
            except KeyError:
                ws_users[self.scope["user"].id] = [self]
            await self.send({"type": "websocket.accept"})
        else:
            await self.send({"type": "websocket.reject"})
            # print(ws_users)

    async def websocket_receive(self, event):
        print('Websocket received...', event)
        data = json.loads(event["text"])
        try:
            for ws_user in ws_users[data["to"]]:
                await ws_user.send({
                    "type": "websocket.send",
                    "text": json.dumps({"from": self.scope["user"].id, "type": data["type"], "msg": data["msg"]}),
                })
        except KeyError:
            pass
        # await self.send({
        #     "type": "websocket.send",
        #     "text": event["text"],
        # })
        if data["type"] >= 0:
            await database_sync_to_async(Chat.objects.create)(
                user1_id=self.scope["user"].id, type=data["type"], msg=data["msg"],
                user2_id=data["to"]
            )
        elif data["type"] == -1:
            pass

    async def websocket_disconnect(self, event):
        print('Websocket disconnected...', event)
        if self.scope["user"].is_authenticated:
            ws_users[self.scope["user"].id].remove(self)
            if len(ws_users[self.scope["user"].id]) == 0:
                del ws_users[self.scope["user"].id]

        # print(ws_users)
        raise StopConsumer()
