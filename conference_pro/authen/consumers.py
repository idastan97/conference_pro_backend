import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

from .models import User_settings


class PeersConsumer(AsyncConsumer):

    def __init__(self, scope):
        super().__init__(scope)
        self.user_id = None
        self.group_id = None

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
            self.user_id = user.id
            self.group_id = str(user.id)
            user_settings = User_settings.objects.get(user=user)
            user_settings.status = 1
            user_settings.save()
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
            self.group_id = str(machine_id)
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
            machine_settings = User_settings.objects.get(user_id=int(machine_id))
            machine_settings.status = 0
            machine_settings.save()

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self, event):
        if self.user_id:
            user_settings = User_settings.objects.get(user_id=int(self.group_id))
            user_settings.status = 0
            user_settings.save()
            res = json.dumps({
                'method': "client_off",
            })
        else:
            user_settings = User_settings.objects.get(user_id=int(self.group_id))
            user_settings.status = 1
            user_settings.save()
            res = json.dumps({
                'method': "client_off",
            })
        # print("      reeeeeees")
        # print(type(res))
        await self.channel_layer.group_send(
            str(self.group_id),
            {
                "type": "chat_message",
                'text': res,
            }
        )
