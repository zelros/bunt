# -*- coding: utf-8 -*-

"""
For each API you want to evaluate, you have to create an account and complete the credentials.
You can let all the parameters of the APIs you are not using to None.
If you want to add your own api, add description to your credentials
"""

"""
apiai

To use ApiAi, you have to create one agent for every language you want to test it on.
Then put your developper access token for each agent
"""
APIAI_TOKENS = {
    'en': '',
    'fr': ''
}

"""
luis

To use Luis, there is no need to create agents. Only put your key.
"""
LUIS_KEY = ''

"""
Recast

To use Recast, you have to create one bot. You have to put your user_slug, your bot_slug and your token
"""
RECAST_USER_SLUG = ''
RECAST_BOT_SLUG = ''
RECAST_TOKEN = ''

