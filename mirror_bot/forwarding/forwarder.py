from models import TelegramWebhook
from mirror_bot.db.database import has_group_pair, create_message_pair, get_forwarded_id, create_member_ship, is_whitelisted
from telegram import Bot
from telegram.error import TelegramError

class Forwarder:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.message = webhook_data.message
        self.target_group_id = None
        self.status = None
        
        create_member_ship(self.message['chat']) 
        self.is_whitelisted = False
        if is_whitelisted(int(self.message['from']['id'])):
            self.is_whitelisted = True
        if not self.is_whitelisted:
            if 'username' in self.message['from']:
                self.is_whitelisted = is_whitelisted(self.message['from']['username'])
    def get_pair_group(self):
        return get_target_group_id(self.message['chat']['id'])

    async def forward(self): 
        if not self.is_whitelisted:
            return 
        try:
            self.target_group_id = self.get_pair_group()
            if not self.target_group_id:
                print("No match found")
                return 

            if "text" in self.message:
                await self.handle_text_forward()
            else:
                await self.handle_media_forward()

            if self.status:
                create_message_pair(
                    from_group_id=self.message['chat']['id'],
                    to_group_id=self.target_group_id,
                    original_id=self.message['message_id'],
                    forwarded_id=self.status.message_id
                )
        except TelegramError as e:
            print(f"Telegram error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    async def handle_text_forward(self):
        reply_to_message = self.message.get('reply_to_message')
        if reply_to_message:
            corresponding_message_id = self.get_corresponding_message_id(reply_to_message)
            if corresponding_message_id:
                self.status = await self.bot.send_message(
                    chat_id=self.target_group_id, 
                    text=self.message['text'], 
                    reply_to_message_id=corresponding_message_id
                )
            else:
                await self.forward_as_reply_with_preview(reply_to_message)
        else:
            self.status = await self.bot.send_message(
                chat_id=self.target_group_id, 
                text=self.message['text']
            )

    def get_corresponding_message_id(self, reply_to_message):
        from_group_id = self.message['chat']['id']
        to_group_id = self.target_group_id

        corresponding_message_id = get_forwarded_id(
            from_group_id=from_group_id, 
            to_group_id=to_group_id, 
            original_id=reply_to_message['message_id']
        )
        if not corresponding_message_id:
            corresponding_message_id = get_forwarded_id(
                from_group_id=to_group_id, 
                to_group_id=from_group_id, 
                forwarded_id=reply_to_message['message_id']
            )
        return corresponding_message_id

    async def forward_as_reply_with_preview(self, reply_to_message):
        '''use this is the corresponding reply message is not found'''
        original_message_preview = reply_to_message.get('text', '')[:100]
        reply_message = (
            f"*🔄 {reply_to_message['from']['first_name']}*:\n"
            f"{original_message_preview}...\n\n"
            f"{self.message['text']}"
        )
        self.status = await self.bot.send_message(
            chat_id=self.target_group_id,
            text=reply_message,
            parse_mode='Markdown'
        )

    async def handle_media_forward(self):
        media_handlers = [
            ('photo', self.send_photo),
            ('video', self.send_video),
            ('document', self.send_document),
            ('audio', self.send_audio),
            ('voice', self.send_voice),
            ('animation', self.send_animation),
            ('sticker', self.send_sticker),
            ('location', self.send_location),
            ('venue', self.send_venue),
            ('contact', self.send_contact),
            ('poll', self.send_poll),
            ('video_note', self.send_video_note)
        ]

        for media_type, handler in media_handlers:
            if media_type in self.message:
                await handler()

    async def send_photo(self):
        photo = self.message['photo'][-1]['file_id']
        caption = self.message.get('caption')
        self.status = await self.bot.send_photo(chat_id=self.target_group_id, photo=photo, caption=caption)

    async def send_video(self):
        video = self.message['video']
        self.status = await self.bot.send_video(
            chat_id=self.target_group_id, 
            video=video['file_id'], 
            caption=self.message.get('caption'),
            duration=video.get('duration'), 
            width=video.get('width'), 
            height=video.get('height')
        )

    async def send_document(self):
        document = self.message['document']
        self.status = await self.bot.send_document(
            chat_id=self.target_group_id, 
            document=document['file_id'], 
            caption=self.message.get('caption'),
            filename=document.get('file_name')
        )

    async def send_audio(self):
        audio = self.message['audio']
        self.status = await self.bot.send_audio(
            chat_id=self.target_group_id, 
            audio=audio['file_id'], 
            caption=self.message.get('caption'),
            duration=audio.get('duration')
        )

    async def send_voice(self):
        voice = self.message['voice']
        self.status = await self.bot.send_voice(
            chat_id=self.target_group_id, 
            voice=voice['file_id'], 
            duration=voice.get('duration')
        )

    async def send_animation(self):
        animation = self.message['animation']
        self.status = await self.bot.send_animation(
            chat_id=self.target_group_id, 
            animation=animation['file_id'], 
            caption=self.message.get('caption')
        )

    async def send_sticker(self):
        sticker = self.message['sticker']
        self.status = await self.bot.send_sticker(chat_id=self.target_group_id, sticker=sticker['file_id'])

    async def send_location(self):
        location = self.message['location']
        self.status = await self.bot.send_location(
            chat_id=self.target_group_id, 
            latitude=location['latitude'], 
            longitude=location['longitude']
        )

    async def send_venue(self):
        venue = self.message['venue']
        self.status = await self.bot.send_venue(
            chat_id=self.target_group_id, 
            latitude=venue['location']['latitude'], 
            longitude=venue['location']['longitude'],
            title=venue['title'], 
            address=venue['address']
        )

    async def send_contact(self):
        contact = self.message['contact']
        self.status = await self.bot.send_contact(
            chat_id=self.target_group_id, 
            phone_number=contact['phone_number'], 
            first_name=contact['first_name']
        )

    async def send_poll(self):
        poll = self.message['poll']
        options = [option['text'] for option in poll['options']]
        self.status = await self.bot.send_poll(
            chat_id=self.target_group_id, 
            question=poll['question'], 
            options=options
        )

    async def send_video_note(self):
        video_note = self.message['video_note']
        self.status = await self.bot.send_video_note(
            chat_id=self.target_group_id, 
            video_note=video_note['file_id'], 
            duration=video_note.get('duration')
        )


def get_target_group_id(chat_id):
    return has_group_pair(chat_id)