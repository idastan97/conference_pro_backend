import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

from .models import User_settings


class PeersConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({"type": "websocket.accept"})
        # print(self.channel_layer)
        await self.send({
            "type": "websocket.send",
            'text': "first hello",
        })

    async def websocket_receive(self, event):
        print("receive", event)
        data = json.loads(event['text'])
        if data['method'] == 'register_machine':
            user = Token.objects.get(key=data['token']).user
            print(user.id)
            print(type(user.id))
            # print(self.channel_layer)
            await self.channel_layer.group_add(
                str(user.id),
                self.channel_name,
            )
        elif data['method'] == 'connect_machine':
            print("   -----------------")
            # print(data)
            peer_id = data['peer_id']
            print(type(peer_id))
            machine_id = data['machine_id']
            await self.channel_layer.group_add(
                str(machine_id),
                self.channel_name,
            )
            res = json.dumps({
                'peer_id': peer_id,
                'method': "connect_to_peer",
            })
            print("      reeeeeees")
            print(type(res))
            await self.channel_layer.group_send(
                str(machine_id),
                {
                        "type": "chat_message",
                        'text': res,
                }
            )

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self, event):
        print("disconeected", event)
