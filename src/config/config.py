# @BotFather Token
TELEGRAM_TOKEN = ''

# Bot username, example: VaultCloudBot
# Use plain name only (no @, no URL)
TELEGRAM_USERNAME = 'VaultCloudBot'.lower().replace('@', '')

# Random 1-256 characters token to ensure that the request comes from the telegram
# (it should be the same as setWebHook secret_token)
TELEGRAM_SECRET_TOKEN = ''

# Used for bug reports - do not edit this chat id
DEVELOPER_CHAT_ID = 854032047

# ACCESS CONFIGS
ADMIN_CHAT_ID = 854032047

# Database Connection
DB_ADDR = 'localhost'
DB_NAME = ''
DB_USER = ''
DB_PASS = ''

# DO NOT CHANGE/RENAME 'VALID_ACCESSIBILITY'
VALID_ACCESSIBILITY = ('DEVELOPER', 'ADMIN', 'USER', 'RESTRICTED', 'BLOCK')
