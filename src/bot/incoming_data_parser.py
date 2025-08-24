class TelegramIncomingDataParser:
    def __init__(self, message):
        # Raw Telegram update payload
        self.message = message

        # Common fields
        self.member_info = {}
        self.member_id = None
        self.chat_id = None
        self.is_here = 'main_menu'
        self.chat_method = None
        self.chat_type = None
        self.user_id = None
        self.username = ''
        self.first_name = ''
        self.last_name = ''
        self.text = ''
        self.caption = ''
        self.accessibility = 'USER'

        # Media fields
        self.photo = []
        self.video_id = ''
        self.audio_id = ''
        self.document_id = ''
        self.sticker_id = ''
        self.voice_id = ''
        self.animation_id = ''
        self.contact = {}
        self.location = {}
        self.poll = {}

        # Callback query fields
        self.callback = ''
        self.callback_query_id = ''
        self.callback_message_text = ''

        # Detect update type and parse accordingly
        if message.get('message', {}).get('from', {}).get('id', 0) > 0:
            self.__message()
        elif message.get('callback_query', {}).get('from', {}).get('id', 0) > 0:
            self.__callback_query()
        elif message.get('edited_message', {}).get('from', {}).get('id', 0) > 0:
            self.__edited_message()

    def __message(self):
        """Parse standard incoming message"""
        msg = self.message.get('message', {})

        # Chat and user info
        self.chat_id = msg.get('chat', {}).get('id', 0)
        self.chat_method = 'message'
        self.chat_type = msg.get('chat', {}).get('type', 'private')
        self.user_id = msg.get('from', {}).get('id', 0)
        self.username = msg.get('from', {}).get('username', '')
        self.first_name = msg.get('from', {}).get('first_name', '')
        self.last_name = msg.get('from', {}).get('last_name', '')

        # Content
        self.text = msg.get('text', '')
        self.caption = msg.get('caption', '')

        # Media
        self.photo = msg.get('photo', [])
        self.video_id = msg.get('video', {}).get('file_id', '')
        self.audio_id = msg.get('audio', {}).get('file_id', '')
        self.document_id = msg.get('document', {}).get('file_id', '')
        self.sticker_id = msg.get('sticker', {}).get('file_id', '')
        self.voice_id = msg.get('voice', {}).get('file_id', '')
        self.animation_id = msg.get('animation', {}).get('file_id', '')

        # Other types
        self.contact = msg.get('contact', {})
        self.location = msg.get('location', {})
        self.poll = msg.get('poll', {})

    def __callback_query(self):
        """Parse callback_query (button presses)"""
        cb = self.message.get('callback_query', {})

        # User and chat
        self.chat_id = cb.get('message', {}).get('chat', {}).get('id', 0)
        self.chat_method = 'callback'
        self.chat_type = cb.get('message', {}).get('chat', {}).get('type', 'private')
        self.user_id = cb.get('from', {}).get('id', 0)
        self.username = cb.get('from', {}).get('username', '')
        self.first_name = cb.get('from', {}).get('first_name', '')
        self.last_name = cb.get('from', {}).get('last_name', '')

        # Callback data
        self.callback = cb.get('data', '')
        self.callback_query_id = cb.get('id', '')
        self.callback_message_text = cb.get('message', {}).get('text', '')

    def __edited_message(self):
        """Parse edited_message"""
        emsg = self.message.get('edited_message', {})

        self.chat_id = emsg.get('chat', {}).get('id', 0)
        self.chat_method = 'message_edit'
        self.chat_type = emsg.get('chat', {}).get('type', 'private')
        self.user_id = emsg.get('from', {}).get('id', 0)
        self.username = emsg.get('from', {}).get('username', '')
        self.first_name = emsg.get('from', {}).get('first_name', '')
        self.last_name = emsg.get('from', {}).get('last_name', '')

        self.text = emsg.get('text', '')
        self.caption = emsg.get('caption', '')
