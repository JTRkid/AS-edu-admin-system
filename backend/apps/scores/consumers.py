import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ScoreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle client messages if needed
        pass

    async def score_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'score.updated',
            'student_id': event.get('student_id'),
            'chapter_no': event.get('chapter_no'),
            'section_no': event.get('section_no'),
            'score': event.get('score'),
        }))
