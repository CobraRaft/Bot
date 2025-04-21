import asyncio
import random
from collections import defaultdict

import requests
import discord
from yt_dlp import YoutubeDL
from discord import app_commands
from discord.ext import commands

if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so.0')
    print("Opus loaded?", discord.opus.is_loaded())
else:
    print("Opus not loaded.")

intents = discord.Intents.all()  # Remember to adjust these in the Developer Portal!
bot = commands.Bot(command_prefix="/", intents=intents)

user_xp = defaultdict(int)
user_levels = defaultdict(int)
ticket_channels = {}
user_level_cooldown = defaultdict(float)
LEVEL_UP_COOLDOWN = 5  # seconds

# Set Streaming Status
@bot.event
async def on_ready():

    status_channel = discord.utils.get(bot.get_all_channels(), name="📡・bot-status")
    if status_channel:
        # Send a embed to status channel for bot status and commands sync ect..
        embed = discord.Embed(title="Bot Status", description="Bot is online and ready to go!", color=discord.Color.green())
        embed.add_field(name="Status", value="**Online with Stramer Mode !**")
        embed.add_field(name="Commands", value=f"**{len(bot.tree.get_commands())} Commands Synced !**.")
        embed.add_field(name="Ping", value=f"**{round(bot.latency * 1000)}ms**")
        embed.add_field(name="Guilds", value=len(bot.guilds))
        embed.add_field(name="Users", value=len(bot.users))
        embed.set_thumbnail(url=bot.user.avatar.url)
        await status_channel.send(embed=embed)
        await status_channel.send("**📡 Bot is online and ready to go!**")
   
    
    await bot.change_presence(activity=discord.Streaming(name="Spaff Stream...", url="https://twitch.tv/discord"))
    try:
        synced = await bot.tree.sync()
        print(f"[✓] Synced {len(synced)} slash commands.")
                
    except Exception as e:
        print(f"[!] Error syncing commands: {e}")
    print(f"[✓] Logged in as {bot.user}")

# ---------------------------- MODERATION ----------------------------
@bot.tree.command(name="ban", description="Ban a member")
@app_commands.describe(member="The member to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member.mention} has been banned. Reason: {reason}")

@bot.tree.command(name="kick", description="Kick a member")
@app_commands.describe(member="The member to kick", reason="Reason for kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member.mention} has been kicked. Reason: {reason}")

@bot.tree.command(name="mute", description="Mute a member")
@app_commands.describe(member="The member to mute")
async def mute(interaction: discord.Interaction, member: discord.Member):
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
    await member.add_roles(mute_role)
    await interaction.response.send_message(f"🔇 {member.mention} has been muted.")

@bot.tree.command(name="clear", description="Clear messages")
@app_commands.describe(amount="Number of messages to clear")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Cleared {amount} messages!", ephemeral=True)

@bot.tree.command(name="warn", description="Warn a user")
@app_commands.describe(member="Member to warn", reason="Reason for warning")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    await interaction.response.send_message(f"⚠️ {member.mention} has been warned. Reason: {reason}")

@bot.tree.command(name="lock", description="Lock a channel")
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel locked.")

@bot.tree.command(name="slowmode", description="Set slowmode in a channel")
@app_commands.describe(seconds="Delay in seconds")
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"🐢 Slowmode set to {seconds} seconds.")




# ---------------------------- FUN ----------------------------
@bot.tree.command(name="meme", description="Sends a random meme")
async def meme(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        response = requests.get('https://meme-api.com/gimme')
        if response.status_code == 200:
            meme_data = response.json()
            embed = discord.Embed(title=meme_data['title'])
            embed.set_image(url=meme_data['url'])
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Failed to fetch meme, try again later!")
    except Exception as e:
        await interaction.followup.send("Error fetching meme, try again later!")

@bot.tree.command(name="8ball", description="Ask the magic 8ball a question")
@app_commands.describe(question="Your question")
async def _8ball(interaction: discord.Interaction, question: str):
    responses = ["Yes", "No", "Maybe", "Definitely", "Ask again later"]
    await interaction.response.send_message(f"🎱 {random.choice(responses)}")

@bot.tree.command(name="joke", description="Get a random joke")
async def joke(interaction: discord.Interaction):
    jokes = ["Why did the chicken join a band? Because it had drumsticks!", "I'm on a seafood diet. I see food and I eat it."]
    await interaction.response.send_message(random.choice(jokes))

@bot.tree.command(name="rps", description="Play rock paper scissors")
@app_commands.describe(choice="rock, paper or scissors")
async def rps(interaction: discord.Interaction, choice: str):
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)
    await interaction.response.send_message(f"You chose {choice}, I chose {bot_choice}!")

@bot.tree.command(name="rate", description="Rate something")
@app_commands.describe(thing="What should I rate?")
async def rate(interaction: discord.Interaction, thing: str):
    score = random.randint(1, 10)
    await interaction.response.send_message(f"I rate {thing} a {score}/10!")

@bot.tree.command(name="roast", description="Roast someone")
@app_commands.describe(user="User to roast")
async def roast(interaction: discord.Interaction, user: discord.Member):
    roasts = ["You're the reason the gene pool needs a lifeguard.", "You bring everyone so much joy... when you leave the room."]
    await interaction.response.send_message(f"🔥 {user.mention}, {random.choice(roasts)}")

@bot.tree.command(name="discodance", description="Party time!")
async def discodance(interaction: discord.Interaction):
    await interaction.response.send_message("🪩💃 Let's dance! DiscoBot brings the party! 🕺🪩")

@bot.tree.command(name="vibecheck", description="Check the vibe of the server")
async def vibecheck(interaction: discord.Interaction):
    vibe = random.randint(1, 10)
    await interaction.response.send_message(f"🕺 Vibe Check: {vibe}/10")

@bot.tree.command(name="epicfact", description="Get an epic fun fact")
async def epicfact(interaction: discord.Interaction):
    facts = ["Bananas are berries, but strawberries aren't.", "Honey never spoils.", "Octopuses have three hearts."]
    await interaction.response.send_message(f"🧠 Did you know? {random.choice(facts)}")

# Generate image with JeyyApi Api Key and send it to the channel
# Generate image with JeyyApi Api Key and send it to the channel
@bot.tree.command(name="generate", description="Generate an image")
@app_commands.describe(prompt="What should I generate?")
async def generate(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()  # Acknowledge the interaction
    try:
        print(f"Generating image for prompt: {prompt}")  # Log the prompt being sent.

        response = requests.post('https://api.jeyy.xyz/generate', 
                                 json={'prompt': prompt}, 
                                 headers={'Authorization': '64OJ0E9O68P32CPL6GSJ0CPH6GPJ4CG.ADO62PJ6.TTxjgp95VuyJ2uh6-MJ_uQ'})

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            image_data = response.json()
            if 'url' in image_data:
                embed = discord.Embed(title=prompt)
                embed.set_image(url=image_data['url'])
                await interaction.followup.send(embed=embed)  # Use followup to send the image
            else:
                await interaction.followup.send("No image URL found in the response.")
        else:
            await interaction.followup.send(f"Failed to generate image. Status code: {response.status_code}, Error: {response.text}")

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")
    
# ---------------------------- UTILITY ----------------------------
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

@bot.tree.command(name="userinfo", description="Get user info")
@app_commands.describe(user="The user to inspect")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"Info for {user}", color=discord.Color.blurple())
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Joined", value=user.joined_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    await interaction.response.send_message(embed=embed)
    


# ---------------------------- INVITE SYSTEM ----------------------------
@bot.tree.command(name="invites", description="Check your invites")
async def invites(interaction: discord.Interaction):
    invites = await interaction.guild.invites()
    total = sum(1 for i in invites if i.inviter == interaction.user)
    await interaction.response.send_message(f"📨 You've invited {total} members!")

# ---------------------------- TICKET SYSTEM ----------------------------
@bot.tree.command(name="ticket", description="Create a support ticket")
async def ticket(interaction: discord.Interaction):
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
    ticket_channels[interaction.user.id] = channel.id
    await interaction.response.send_message(f"🎫 Ticket created: {channel.mention}", ephemeral=True)

@bot.tree.command(name="close", description="Close your ticket")
async def close(interaction: discord.Interaction):
    if interaction.channel.id in ticket_channels.values():
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("❌ This is not a ticket channel.", ephemeral=True)

# ---------------------------- STATS ----------------------------
@bot.tree.command(name="stats", description="Get bot statistics")
async def stats(interaction: discord.Interaction):
    await interaction.response.send_message(f"🤖 Connected to {len(bot.guilds)} servers with {len(bot.users)} users.")


# ---------------------------- WEBSITE COMMAND ----------------------------
@bot.tree.command(name="website", description="Get the bot's website")
async def website(interaction: discord.Interaction):
    await interaction.response.send_message("🌐 Visit our website at https://spaff.xyz")


# ---------------------------- SUPPORT COMMAND ----------------------------
@bot.tree.command(name="support", description="Get support for the bot")
async def support(interaction: discord.Interaction):
    await interaction.response.send_message("🛠️ Need support? Join our support server at https://discord.gg/spaff")
    await interaction.response.send_message("🛠️ Or contact us on Twitter @SpaffBot")
    await interaction.response.send_message("🛠️ Or contact us on Instagram @SpaffBot")
    await interaction.response.send_message("🛠️ Or contact us on our Gmail spaffbot.com@gmail.com")
    await interaction.response.send_message("🛠️ Or create a ticket on our Discord")

# ---------------------------- SET LOGS IN A CHANNEL ID WITH COMMAND ----------------------------
@bot.tree.command(name="setlogs", description="Set the logs channel")
@app_commands.describe(channel="The channel to set as logs")
async def setlogs(interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.send_message(f"📜 Logs channel set to {channel.mention}")
    await interaction.response.send_message("📜 Please make sure the bot has permission to send messages in this channel!")
    await interaction.response.send_message("📜 If you have any questions, please ask a moderator.")
    await interaction.response.send_message("📜 Thank you for setting up the logs channel!")
    await interaction.response.send_message("📜 Have a great time on the server!")



# ---------------------------- GIVEAWAY ----------------------------
@bot.tree.command(name="giveaway", description="Start a giveaway")
@app_commands.describe(time="Time for the giveaway", prize="Prize for the giveaway")
async def giveaway(interaction: discord.Interaction, time: str, prize: str):
    await interaction.response.send_message(f"🎉 Giveaway started! Prize: {prize} Time: {time}")
    await interaction.response.send_message("🎉 React with 🎉 to enter!")
    await interaction.response.send_message("🎉 Good luck!")
    await interaction.response.send_message("🎉 The winner will be announced in {time}!")
    await interaction.response.send_message("🎉 If you have any questions, please ask a moderator.")




# ---------------------------- RULES EMBED ----------------------------
@bot.tree.command(name="rules", description="Get the server rules")
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(title="Server Rules", description="Please follow these rules:", color=discord.Color.blurple())
    embed.add_field(name="Rule 1", value="Be respectful to all members.")
    embed.add_field(name="Rule 2", value="No spamming or flooding.")
    embed.add_field(name="Rule 3", value="No NSFW content.")
    await interaction.response.send_message(embed=embed)
    await interaction.response.send_message("📜 Here are the server rules!")
    await interaction.response.send_message("📜 Please follow these rules!")
    await interaction.response.send_message("📜 If you break a rule, you will be warned or kicked/banned.")
    await interaction.response.send_message("📜 Thank you for reading the rules!")
    await interaction.response.send_message("📜 Have a great time on the server!")
    await interaction.response.send_message("📜 If you have any questions, please ask a moderator.")
    

# ---------------------------- HELP WITH EMBED ----------------------------
@bot.tree.command(name="help", description="Get help with the bot")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", description="Here are the commands you can use:", color=discord.Color.blurple())
    embed.add_field(name="Moderation", value="ban, kick, mute, clear, warn, lock, slowmode")
    embed.add_field(name="Fun", value="meme, 8ball, joke, rps, rate, roast, discodance, vibecheck, epicfact")
    embed.add_field(name="Utility", value="ping, userinfo, invites, ticket, close, stats")
    embed.add_field(name="Leveling", value="rank")
    embed.add_field(name="Music", value="play, stop, leave")
    await interaction.response.send_message(embed=embed)
    await interaction.response.send_message("📚 Here are the commands you can use!")



# ---------------------------- SERVER INFO ----------------------------
@bot.tree.command(name="serverinfo", description="Get server info")
async def serverinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="Server Info", description="Here is the server info:", color=discord.Color.blurple())
    embed.add_field(name="Name", value=interaction.guild.name)
    embed.add_field(name="ID", value=interaction.guild.id)
    embed.add_field(name="Owner", value=interaction.guild.owner)
    embed.add_field(name="Members", value=interaction.guild.member_count)
    embed.add_field(name="Created", value=interaction.guild.created_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else interaction.guild.default_icon.url)
    await interaction.response.send_message(embed=embed)
    await interaction.response.send_message("📜 Here is the server info!")
    await interaction.response.send_message("📜 If you have any questions, please ask a moderator.")
    await interaction.response.send_message("📜 Thank you for using the server info command!")
    await interaction.response.send_message("📜 Have a great time on the server!")
    




# ---------------------------- WEBHOOKS ----------------------------
@bot.tree.command(name="webhook", description="Create a webhook")
@app_commands.describe(name="Webhook name", avatar="Webhook avatar URL")
async def webhook(interaction: discord.Interaction, name: str, avatar: str):
    await interaction.response.send_message(f"🔗 Webhook created! Name: {name} Avatar: {avatar}")
    await interaction.response.send_message("🔗 Please make sure the bot has permission to create webhooks!")
    await interaction.response.send_message("🔗 If you have any questions, please ask a moderator.")
    await interaction.response.send_message("🔗 Thank you for creating a webhook!")
    await interaction.response.send_message("🔗 Have a great time on the server!")


# --------------------------- BOT ERROR / LOGS IN CHANNEL NAME : "📛・bot-errors" ----------------------------
@bot.event
async def on_command_error(ctx, error):
    error_channel = discord.utils.get(ctx.guild.text_channels, name="📛・bot-errors")
    if error_channel:
        await error_channel.send(f"📛 Error: {error}")
        await ctx.send("📛 An error occurred. Please check the bot errors channel for more info.")
        await ctx.send("📛 If you have any questions, please ask a moderator.")
        await ctx.send("📛 Thank you for reporting the error!")
        await ctx.send("📛 Have a great time on the server!")


# ---------------------------- LEVELING ----------------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_xp[message.author.id] += 5
    xp = user_xp[message.author.id]
    level = xp // 100
    if level > user_levels[message.author.id]:
        user_levels[message.author.id] = level
        now = asyncio.get_event_loop().time()
        if now - user_level_cooldown[message.author.id] > LEVEL_UP_COOLDOWN:
            await message.channel.send(f"🎉 {message.author.mention} leveled up to {level}!")
            user_level_cooldown[message.author.id] = now
    await bot.process_commands(message)

@bot.tree.command(name="rank", description="Show your level and XP")
async def rank(interaction: discord.Interaction):
    xp = user_xp[interaction.user.id]
    level = user_levels[interaction.user.id]
    await interaction.response.send_message(f"📈 {interaction.user.mention} — Level: {level}, XP: {xp}")

# ---------------------------- WELCOME / AUTOROLE ----------------------------
@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome" or "📥・guild-join")
    if welcome_channel:
        await welcome_channel.send(f"👋 Welcome {member.mention} to the server!")
    role = discord.utils.get(member.guild.roles, name="Members")
    if role:
        await member.add_roles(role)


# ---------------------------- GOODBYE ----------------------------
@bot.event
async def on_member_remove(member):
    goodbye_channel = discord.utils.get(member.guild.text_channels, name="goodbye" or "📤・guild-leave")
    if goodbye_channel:
        await goodbye_channel.send(f"👋 Goodbye {member.name}, we will miss you!")
                

# ---------------------------- MUSIC ----------------------------
music_queue = {}

@bot.tree.command(name="play", description="Play a song from YouTube")
@app_commands.describe(url="YouTube URL")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Tu dois être dans un salon vocal pour jouer une musique !", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel

    if not interaction.guild.voice_client:
        vc = await voice_channel.connect()
    else:
        vc = interaction.guild.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        title = info.get('title', 'Unknown Title')

    ffmpeg_options = {
        'options': '-vn'
    }

    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))

    await interaction.response.send_message(f"🎶 Now playing: **{title}**")

@bot.tree.command(name="stop", description="Stop the music")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏹️ Music stopped.")

@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Left the voice channel.")

bot.run("MTM2Mjc1Mzk2NDI1NjI2ODUwOQ.Ge7YNZ.__jtBF48VBT21Twa1CCUOIle306u2EigKXc9qc")
