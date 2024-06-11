import logging
import discord
from discord.ext import commands

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)

# Intentsの設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # メッセージの内容にアクセス
intents.guilds = True
intents.members = True  # メンバー情報にアクセス

bot = commands.Bot(command_prefix='IMA!', intents=intents, help_command=None)
important_users = set()

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    print(f'Logged in as {bot.user}')

@bot.command()
async def add(ctx, user_id: str):
    if user_id.startswith('<@') and user_id.endswith('>'):
        user_id = user_id[2:-1]
        if user_id.startswith('!'):
            user_id = user_id[1:]
    try:
        user_id = int(user_id)
    except ValueError:
        await ctx.send("Invalid user ID or mention.")
        return
    
    important_users.add(user_id)
    user = await bot.fetch_user(user_id)
    response = f'{user.id} ({user.name}) has been added to the important users list.'
    await ctx.send(response)
    logger.info(f'Command "add" executed by {ctx.author.name}: {response}')

@bot.command(name='del')
async def del_user(ctx, user_id: str):
    if user_id.startswith('<@') and user_id.endswith('>'):
        user_id = user_id[2:-1]
        if user_id.startswith('!'):
            user_id = user_id[1:]
    try:
        user_id = int(user_id)
    except ValueError:
        await ctx.send("Invalid user ID or mention.")
        return

    if user_id in important_users:
        important_users.remove(user_id)
        user = await bot.fetch_user(user_id)
        response = f'{user.id} ({user.name}) has been removed from the important users list.'
        await ctx.send(response)
        logger.info(f'Command "del" executed by {ctx.author.name}: {response}')
    else:
        user = await bot.fetch_user(user_id)
        response = f'{user.id} ({user.name}) is not in the important users list.'
        await ctx.send(response)
        logger.warning(f'Command "del" executed by {ctx.author.name}: {response}')

@bot.command()
async def list(ctx):
    if important_users:
        users = [f'{user_id} ({(await bot.fetch_user(user_id)).name})' for user_id in important_users]
        response = 'Important users:\n' + '\n'.join(users)
        await ctx.send(response)
        logger.info(f'Command "list" executed by {ctx.author.name}: Listed important users.')
    else:
        response = 'The important users list is currently empty.'
        await ctx.send(response)
        logger.info(f'Command "list" executed by {ctx.author.name}: {response}')

@bot.command(name='help')
async def custom_help(ctx):
    help_message = (
        'Commands list:\n'
        'IMA!add user_id or @mention - Add user to list\n'
        'IMA!del user_id or @mention - Remove a user from the list\n'
        'IMA!list - View User List\n'
        'IMA!help - View this message\n'
        '@Important Message Alerter - Send "Important message has been sent" to list user'
    )
    await ctx.send(help_message)
    logger.info(f'Command "help" executed by {ctx.author.name}')

@bot.event
async def on_message(message):
    await bot.process_commands(message)  # これを最初に配置

    logger.info(f'Received message: {message.content} from {message.author.name}')
    
    if bot.user in message.mentions or any(role in message.guild.me.roles for role in message.role_mentions if role is not None):
        logger.info(f'Bot was mentioned directly or via role.')
        channel_mention = message.channel.mention
        message_content = message.content
        
        # メンション部分をテキストに変換
        for user in message.mentions:
            message_content = message_content.replace(f'<@{user.id}>', f'@{user.name}')
        for role in message.role_mentions:
            if role in message.guild.me.roles:
                message_content = message_content.replace(f'<@&{role.id}>', f'@{role.name}')

        sent_users = []
        for user_id in important_users:
            user = await bot.fetch_user(user_id)
            await user.send(f"Important message has been sent in {channel_mention}:\n\n{message_content}")
            sent_users.append(user.name)
            logger.info(f'Sent important message to {user.name} due to mention by {message.author.name} in channel {channel_mention}.')
        if sent_users:
            sent_users_list = '\n'.join(sent_users)
            await message.author.send(f"The following users were notified:\n{sent_users_list}")
            logger.info(f'Notified {message.author.name} of sent messages to: {sent_users_list}')


bot.run('TOKEN')