import json
import re
from abc import abstractmethod, ABC

from src.bot.reply_markup import ReplyMarkup
from src.bot.incoming_data_parser import TelegramIncomingDataParser
from src.config.config import TELEGRAM_USERNAME
from src.database.models import Members, Files
from src.bot.telegram_api import TelegramAPI
from src.languages.language import Language
from src.utils.random_string import generate_random_string
from src.utils.validation import get_accessibility


class TelegramBase(TelegramIncomingDataParser, ABC):
    """
    it will call when requests is coming from telegram bot
    """

    def __init__(self, message, environ):
        TelegramIncomingDataParser.__init__(self, message)  # parse incoming data once
        if self.chat_id and self.chat_id is not None:
            self.member_info = Members.check_member_exists(self.chat_id)
            self.load_member_data()

            if self.member_info:
                self.member_info.update_member_info(
                    username=self.username,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    accessibility=self.accessibility,
                )
            self.telegram_api = TelegramAPI()
            self.language = Language().data
            self.replyMarkup = ReplyMarkup(self.language, self.accessibility)
            self.environ = environ

    def load_member_data(self):
        self.member_id = self.member_info.id
        self.is_here = self.member_info.is_here
        self.accessibility = get_accessibility(
            chat_id=self.chat_id,
            username=self.username,
            accessibility=self.member_info.accessibility
        )

    @staticmethod
    def create(message, environ):
        chat_type = message.get('chat', {}).get('type', 'private')
        if chat_type == 'private':
            return TelegramTypePrivate(message, environ)
        elif chat_type in ('group', 'supergroup'):
            return TelegramTypeGroup(message, environ)
        elif chat_type == 'channel':
            return TelegramTypeChannel(message, environ)
        return None

    @abstractmethod
    def user_section(self):
        pass

    @property
    def photo_id(self):
        _photo_id = ''
        photos = self.message.get('message', {}).get('photo', [])
        if photos:
            _photo_id = max(photos, key=lambda p: p.get('file_size', 0)).get('file_id', '')
        return _photo_id

    @property
    def is_block(self):
        return self.accessibility not in ('USER', 'ADMIN', 'DEVELOPER')

    @property
    def is_admin(self):
        return self.accessibility == 'ADMIN'

    @property
    def is_developer(self):
        return self.accessibility == 'DEVELOPER'

    @staticmethod
    def create_public_unique_url(db_id):
        return f'https://t.me/{TELEGRAM_USERNAME}/?start=file_{db_id}'


class TelegramTypePrivate(TelegramBase):
    """
    it will call when requests is in Private Bot Chat
    """

    def __init__(self, message, environ):
        super().__init__(message, environ)
        self.__maximum_files_for_each_files_record = 10
        if self.chat_method in ('message', 'callback') and self.is_block is False:
            self.user_section()

    def __send_wrong_command(self):
        self.telegram_api.send_message(
            chat_id=self.chat_id,
            text=self.language.get('global_section', {}).get('wrong_command', 'Wrong Command'),
            reply_markup=self.replyMarkup.start()
        )

    def handle_add_a_new_file_finish(self, __db_recent_files_id, __db_id):
        Files.update(status='100').where(Files.id == __db_id).execute()
        self.telegram_api.send_message(
            chat_id=self.chat_id,
            text=self.language.get('admin_section', {}).get(
                'add_a_new_file_finish_message', 'Send next file'
            ).replace('%file_count%', str(len(__db_recent_files_id)))
            .replace('%unique_url%', self.create_public_unique_url(__db_id)),
            reply_markup=self.replyMarkup.admin()
        )

    def handle_add_a_new_file(self, __db_id=None):

        __correct_file = True
        __db_data = None
        __file_method = None
        __file_id = None
        __db_recent_files_id = []
        if __db_id:
            __db_data = Files.select(Files.file_ids).where(Files.id == __db_id).first()
            __db_recent_files_id = __db_data.get_file_ids()

        if self.text in (
                self.language.get('admin_section', {}).get(
                    'add_a_new_file_finish_button', '/admin_add_a_new_file_finish'
                ), '/admin_add_a_new_file_finish'):
            self.handle_add_a_new_file_finish(__db_recent_files_id, __db_id)
            return

        if self.photo_id:
            __file_method = 'photo'
            __file_id = self.photo_id
        elif self.text:
            __file_method = 'message'
            __file_id = self.text
        elif self.video_id:
            __file_method = 'video'
            __file_id = self.video_id
        elif self.audio_id:
            __file_method = 'audio'
            __file_id = self.audio_id
        elif self.document_id:
            __file_method = 'document'
            __file_id = self.document_id
        elif self.voice_id:
            __file_method = 'voice'
            __file_id = self.voice_id
        elif self.sticker_id:
            __file_method = 'sticker'
            __file_id = self.sticker_id
        elif self.animation_id:
            __file_method = 'animation'
            __file_id = self.animation_id
        else:
            __correct_file = False

        if __correct_file:
            if __db_data is None:
                __db_id = generate_random_string(include_lower=True, include_upper=False, length=16)
                Files.insert(id=__db_id, creator_member_id=self.member_id).execute()
                self.member_info.update_member_info(is_here=f'add_a_new_file_{__db_id}')

            __db_recent_files_id += [{
                'method': __file_method,
                'file_id': __file_id
            }]
            Files.update(file_ids=json.dumps(__db_recent_files_id)).where(Files.id == __db_id).execute()

            if len(__db_recent_files_id) >= self.__maximum_files_for_each_files_record:
                self.handle_add_a_new_file_finish(__db_recent_files_id, __db_id)
            else:
                self.telegram_api.send_message(
                    chat_id=self.chat_id,
                    text=self.language.get('admin_section', {}).get(
                        'add_a_new_file_count_left_allowed', 'Send next file'
                    ).replace(
                        '%left_count%', str(self.__maximum_files_for_each_files_record - len(__db_recent_files_id))
                    ),
                    reply_markup=self.replyMarkup.add_a_new_file_finish_button()
                )
        else:
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('admin_section', {}).get(
                    'add_a_new_file_got_unsupported_data', 'File not supported, Try again'
                ).replace('%left_count%', '9'),
                reply_markup=self.replyMarkup.add_a_new_file_finish_button()
            )

    def user_section(self):
        if self.text in (self.language.get('global_section', {}).get('start_menu_button', '/start'), '/start'):
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('global_section', {}).get('start_message', 'Welcome'),
                reply_markup=self.replyMarkup.start()
            )
        else:
            if self.is_admin or self.is_developer:
                self.admin_section()
            else:
                self.__send_wrong_command()

    def admin_section(self):
        if self.text in (self.language.get('admin_section', {}).get('admin_menu_button', '/admin'), '/admin'):
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('admin_section', {}).get('admin_menu_message', 'Welcome to Admin Menu'),
                reply_markup=self.replyMarkup.admin()
            )
        elif self.text == self.language.get('admin_section', {}).get('add_a_new_file', '/admin_add_new_file'):
            self.member_info.update_member_info(is_here='add_a_new_file')
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('admin_section', {}).get('add_a_new_file_message', 'Send your files'),
                reply_markup=self.replyMarkup.return_to_admin()
            )
        elif m := re.search(r'^add_a_new_file(?:_(\w+))?$', self.is_here):
            self.handle_add_a_new_file(m.group(1))
        else:
            if self.is_developer:
                self.developer_section()
            else:
                self.__send_wrong_command()

    def developer_section(self):
        if self.text == '/developer':
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('developer_menu_message', 'Welcome to Developer Menu'),
                reply_markup=self.replyMarkup.admin()
            )
        else:
            self.__send_wrong_command()


class TelegramTypeGroup(TelegramBase):
    """
    it will call when requests is in Groups/SuperGroups
    """

    def __init__(self, message, environ):
        super().__init__(message, environ)
        # TODO: group handling

    def user_section(self):
        pass


class TelegramTypeChannel(TelegramBase):
    """
    it will call when requests is in Channels
    """

    def __init__(self, message, environ):
        super().__init__(message, environ)
        # TODO: channel handling

    def user_section(self):
        pass
