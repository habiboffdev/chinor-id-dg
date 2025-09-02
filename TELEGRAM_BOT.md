Opportuni Telegram Bot

1. Telegram bot is for adapting user to new platform. Telegram has a lot of users and they can apply to any evetn without leaving the telegram. It is also used to authenticate along with Google.
2. If they can sign up from telegram, they can login in website also without creating account in website again.
3. Telegram will have minimum features. We can offer user to user telegram web app. For example instead of creating opportunity in dialog, user can press web app button and create opportunity without leaving the app. It applies to user too
4. Telegram bot will have an admin access to opportunites channel that it posts new opportunities as some organizations post. It must follow the SMM rules tho.
5. In the beginning of the bot we offer three languages, ru, en, uz. User will choose and it will be main language until the end of conversation
6. We will use our existing django. We will need to adapt some modals or add models to adapt telegram bot.

Coding Part:

1. We will have different files according to purpose of them. For example, if we use markups we will create markups.py, instead of writing them in the main file. 
2. We will use pyTelegramBotAPI(telebot)
3. We need main object called bot for scalability and better coding experiences. Also We will need to use OOP if tasks are being too large.
4. The bot must work along with Django.

Server part:

Bot will be in the same server with our existing project. But we still need to think about optimizations. We can use webhooks too if needed to speed up. 

MANDATORY:

Everytime you must use Context7 to have latest docs. Don't start any server. I will run myself. Create a new env for the bot.

Strategy:

1. Use a modular approach by separating different functionalities into distinct files (e.g., markups.py for markup-related code). Consider scalability and functionality of the code to future changes.
2. First start with studying the existing Django models and how they can be adapted for the Telegram bot.
3. Think about user experiences in telegram bot and how to make interactions as seamless as possible.

Implementation steps:

1. Student
2. Organization.
3. Admin.