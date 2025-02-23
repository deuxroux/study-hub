from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async #deal with differences between async and models synchronous requirements
from django.contrib.auth import get_user_model
from .models import ChatMessage #save messages


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #this chat feature is one-way between users
        self.user = self.scope["user"]
        self.other_user = self.scope['url_route']['kwargs']['pk'] # so we can access specific users

        # use user IDs to create a custom chat id for the room
        user_ids = sorted([self.user.id, int(self.other_user)])
        self.room_name = f"chat_{'_'.join(map(str, user_ids))}"        
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close() #close session if not authenticated
    
    #leave room
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.scope["user"].id

        if message.strip(): #check to see if message is empty before saving
            await self.save_message(message)

            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,  # Include the sender's ID to update HTML in chat.html
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']  # Get ID from the event

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,  # Send the sender's ID to the client
        }))

#logic for dealing with sync vs async stuff

    async def save_message(self, message):
        sender = self.scope["user"]
        recipient_id = self.scope['url_route']['kwargs']['pk']
        recipient = await database_sync_to_async(User.objects.get)(pk=recipient_id)
        # async_to_sync to utilize the syncronous model
        await database_sync_to_async(ChatMessage.objects.create)(
            sender=sender,
            recipient=recipient,
            message=message
        )