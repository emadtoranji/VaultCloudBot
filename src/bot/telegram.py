from abc import abstractmethod, ABC

from src.bot.reply_markup import ReplyMarkup
from src.bot.incoming_data_parser import TelegramIncomingDataParser
from src.database.models import Members
from src.bot.telegram_api import TelegramAPI
from src.languages.language import Language
from src.utils.validation import get_accessibility


class TelegramBase(TelegramIncomingDataParser, ABC):
    """
    it will call when requests is coming from telegram bot
    """

    def __init__(self, message, environ):
        TelegramIncomingDataParser.__init__(self, message)  # parse incoming data once
        if self.chat_id and self.chat_id is not None:
            self.accessibility = get_accessibility(
                chat_id=self.chat_id,
                username=self.username,
                accessibility=self.member_info.get('accessibility', 'USER')
            )

            self.member_info = Members.check_member_exists(self.chat_id)
            if self.member_info:
                self.member_info.update_member_info(
                    username=self.username,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    accessibility=self.accessibility,
                )

            self.telegram_api = TelegramAPI()
            self.language = Language().data
            self.replyMarkup = ReplyMarkup(self.language)
            self.environ = environ

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
        # else:
        #     return TelegramBase(message, environ)

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


class TelegramTypePrivate(TelegramBase):
    """
    it will call when requests is in Private Bot Chat
    """

    def __init__(self, message, environ):
        super().__init__(message, environ)
        if self.chat_method in ('message', 'callback') and self.is_block is False:
            self.user_section()

    def __send_wrong_command(self):
        self.telegram_api.send_message(
            chat_id=self.chat_id,
            text=self.language.get('wrong_command', 'Wrong Command'),
            reply_markup=self.replyMarkup.start()
        )

    def developer_section(self):
        if self.text == '/developer':
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('developer_menu_message', 'Welcome to Developer Menu'),
                reply_markup=self.replyMarkup.admin()
            )
        else:
            self.__send_wrong_command()

    def admin_section(self):
        if self.text in (self.language.get('admin_menu_button', '/admin'), '/admin'):
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('admin_menu_message', 'Welcome to Admin Menu'),
                reply_markup=self.replyMarkup.admin()
            )
        else:
            if self.is_developer:
                self.developer_section()
            else:
                self.__send_wrong_command()

    def user_section(self):
        if self.text in (self.language.get('start_menu_button', '/start'), '/start'):
            self.telegram_api.send_message(
                chat_id=self.chat_id,
                text=self.language.get('start_message', 'Welcome'),
                reply_markup=self.replyMarkup.start()
            )
        else:
            if self.is_admin or self.is_developer:
                self.admin_section()
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
