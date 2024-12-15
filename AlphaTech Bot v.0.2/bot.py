from tabnanny import check
from unicodedata import name
import discord
import asyncio
from discord.ext import commands
from discord.ui import Button, View
######### v0.2 #########
import sqlite3
######### v0.2 #########


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
ticket_count = 0

## v 0.2 ##
def create_db():
    conn = sqlite3.connect('Alphatech.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS warnings (
        user_id INTEGER,
        guild_id INTEGER,
        warnings INTEGER
    )''')
    conn.commit()
    conn.close()

def add_warning(user_id, guild_id):
    conn = sqlite3.connect('Alphatech.db')
    c = conn.cursor()
    c.execute('SELECT warnings FROM warnings WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
    result = c.fetchone()
    if result:
        warnings = result[0] + 1
        c.execute('UPDATE warnings SET warnings = ? WHERE user_id = ? AND guild_id = ?', (warnings, user_id, guild_id))
    else:
        c.execute('INSERT INTO warnings (user_id, guild_id, warnings) VALUES (?, ?, ?)', (user_id, guild_id, 1))
    conn.commit()
    conn.close()

def get_warnings(user_id, guild_id):
    conn = sqlite3.connect('Alphatech.db')
    c = conn.cursor()
    c.execute('SELECT warnings FROM warnings WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return 0

def remove_warning(user_id, guild_id):
    conn = sqlite3.connect('Alphatech.db')
    c = conn.cursor()
    c.execute('SELECT warnings FROM warnings WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
    result = c.fetchone()
    if result and result[0] > 0:
        warnings = result[0] - 1
        c.execute('UPDATE warnings SET warnings = ? WHERE user_id = ? AND guild_id = ?', (warnings, user_id, guild_id))
        conn.commit()
    conn.close
## v0.2 ##

@bot.event
async def on_ready():
    print(f'The bot {bot.user} is online!')

################################# v0.1 #################################
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Not specified"):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"I could not ban the user. Error: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member: discord.User, *, reason="Not specified"):
    try:
        await ctx.guild.unban(member)
        await ctx.send(f"{member.mention} has been unbanned. Reason: {reason}")
    except Exception as e:  
        await ctx.send(f"I could not unban. Error: {e}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Not specified"):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"I could not kick the user. Error: {e}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I do not have permissions to modify roles.")
        return
    
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role is None:
        mute_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
        
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(mute_role, send_messages=False)
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(mute_role, speak=False)
            
    if mute_role in member.roles:
        await ctx.send(f"{member} is already muted.")
        return
    
    try:
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"{member} has been muted. Reason: {reason if reason else 'No reason'}")
    except discord.Forbidden:
        await ctx.send("I do not have permissions to mute this user.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to mute the user.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, time: int, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I do not have permissions to modify roles.")
        return

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role is None:
        mute_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
        
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(mute_role, send_messages=False)
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(mute_role, speak=False)
    
    if mute_role in member.roles:
        await ctx.send(f"{member} is already muted.")
        return

    try:
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"{member} has been muted for {time} minutes. Reason: {reason if reason else 'No reason.'}")

        await asyncio.sleep(time * 60)

        await member.remove_roles(mute_role)
        await ctx.send(f"{member} has been unmuted after {time} minutes.")
        
    except discord.Forbidden:
        await ctx.send("I do not have permissions to mute this user.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to mute the user.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I do not have permissions to modify roles.")
        return
    
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role is None:
        await ctx.send("The 'Muted' role does not exist on this server.")
        return
    
    if mute_role not in member.roles:
        await ctx.send(f"{member} is not muted.")
        return

    
    try:
        await member.remove_roles(mute_role, reason=reason)
        await ctx.send(f"{member} was unlocked from mute. Reason: {reason if reason else 'No reason.'}")
    except discord.Forbidden:
        await ctx.send("I don't have sufficient permissions to unmute this user.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to unmute this user.")

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = "Available orders",
        description="List of commands you can use",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="!mute <@utilizator> [motiv]", value="mute a user.", inline=False)
    embed.add_field(name="!unmute <@utilizator> [motiv]", value="unmute a user.", inline=False)
    embed.add_field(name="!tempmute <@utilizator> [motiv]", value="tempmute a user", inline=False)
    embed.add_field(name="!ban <@utilizator> [motiv]", value="Ban a user", inline=False)
    embed.add_field(name="!unban <@utilizator> [motiv]", value="Unban a user", inline=False)
    embed.add_field(name="!purge <amount>", value="delete a certain number of messages", inline=False)
    embed.add_field(name="!help", value="displays the list of available commands", inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1:
        await ctx.send("you must specify a number greater than 0", defete_after=5)
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"am sters {amount} mesaje!", delete_after=5)

################################# v0.1 #################################

################################# v0.2 #################################

@bot.command()
async def warn(ctx, user: discord.Member, *, reason=None):
    if ctx.author.guild_permissions.kick_members:
        add_warning(user.id, ctx.guild.id)
        warnings = get_warnings(user.id, ctx.guild.id)
        if reason:
            await ctx.send(f"{user.mention} has been warned for: {reason}. They now have {warnings} warnings.")
        else:
            await ctx.send(f"{user.mention} has been warned. They now have {warnings} warnings.")
    else:
        await ctx.send("You don't have permission to give warnings.")

@bot.command()
async def warnings(ctx, user: discord.Member):
    warnings = get_warnings(user.id, ctx.guild.id)
    await ctx.send(f"{user.mention} has {warnings} warnings.")

@bot.command()
async def delwarn(ctx, user: discord.Member):
    if ctx.author.guild_permissions.kick_members:
        current_warnings = get_warnings(user.id, ctx.guild.id)
        if current_warnings > 0:
            remove_warning(user.id, ctx.guild.id)
            new_warnings = get_warnings(user.id, ctx.guild.id)
            await ctx.send(f"{user.mention} has had a warning removed.They now have {new_warnings} warnings.")
        else:
            await ctx.send(f"{user.metion} has no warnings to remove.")
    else:
        await ctx.send("You don't have permission to remove warnings.")

## ticket system ##

@bot.command()
async def ticketpanel(ctx):
    global ticket_count
    
    embed = discord.Embed(
        title="Support tickets",
        description="Press the button to create a ticket.",
        color=discord.Color.blue()
    )
    
    create_button = Button(label="Create ticket", style=discord.ButtonStyle.green)
    
    async def create_button_callback(interaction):
        global ticket_count
        ticket_count += 1
        
        ticket_name = f"ticket-{ticket_count}"
        
        category = discord.utils.get(interaction.guild.categories, name="Tickets")
        if category is None:
            category = await interaction.guild.create_category("Tickets")
            
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        
        channel = await interaction.guild.create_text_channel(name=ticket_name, category=category, overwrites=overwrites)
        
        await channel.send(f"Hello {interaction.user.mention}! This is your ticket. \nA staff member will respond to your question as soon as possible.")
        
        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)
        
    create_button.callback = create_button_callback

    view = View()
    view.add_item(create_button)

    await ctx.send(embed=embed, view=view)

#ticket commands

@bot.command()
async def add(ctx, ticket_channel: discord.TextChannel, user: discord.Member):
    if ctx.author.guild_permissions.manage_channels or ctx.author == ticket_channel.owner:
        await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
        await ctx.send(f"{user.mention} has been added to the ticket channel {ticket_channel.mention}.")
    else:
        await ctx.send("You do not have permission to add users to this ticket.", ephemeral=True)
  
@bot.command()
async def close(ctx):
    if "ticket-" not in ctx.channel.name:
        await ctx.send("This command can be used only in a ticket channel!")
        return
    embed = discord.Embed(
        title="ticket Closed",
        description="Support team ticket control",
        color=discord.Color.red()
    )          
    
    button_transcript = Button(label="Transcript", style=discord.ButtonStyle.blurple)
    button_reopen = Button(label="Reopen", style=discord.ButtonStyle.green)
    button_delete = Button(label="Delete", style=discord.ButtonStyle.red)
    
    async def transcript_callback(interaction):
            if "ticket-" not in ctx.channel.name:
                await interaction.response.send_message("This command can only be used in a ticket channel!", ephemeral=True)
                return

            transcript_channel = discord.utils.get(ctx.guild.text_channels, name="transcripts")
            if transcript_channel is None:
                transcript_channel = await ctx.guild.create_text_channel(
                    name="transcripts",
                    overwrites={
                        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                    },
                    reason="Creating transcript storage channel"
                )

            messages = [message async for message in ctx.channel.history(limit=None)] 
            messages.reverse()

            transcript_content = "\n".join(
                f"[{message.created_at.strftime('%Y-%m-%d %H: %M:%S')}] {message.author}: {message.content}"
                for message in messages
            )

            if transcript_content.strip() == "":
                await interaction.response.send_message("The ticket is empty. Nothing to save", ephemeral=True)
            else:
                await transcript_channel.send(
                    f"**transcript for {ctx.channel.name}**\n```\n{transcript_content}\n```"
                )
                await interaction.response.send_message("Transcript save succesfully!", ephemeral=True)

    async def reopen_callback(interaction: discord.Interaction):
        if interaction.user == ctx.author:
            await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=False)
            await ctx.channel.set_permissions(ctx.author, read_messages=True)
            await interaction.response.send_message("Ticket reopened", ephemeral=False)
        else:
            await interaction.response.send_message("You don't have permission to reopen ticket", ephemeral=True)

    async def delete_callback(interaction: discord.Interaction):
        if interaction.user == ctx.author:
            await interaction.response.send_message("Ticket will be deleted in 3 seconds..")
            await asyncio.sleep(3)
            await ctx.channel.delete()
        else:
            await interaction.response.send_message("You don't have permission to delete this ticket", ephemeral=True)
            
    button_transcript.callback = transcript_callback
    button_reopen.callback = reopen_callback
    button_delete.callback = delete_callback
    
    view = View()
    view.add_item(button_transcript)
    view.add_item(button_reopen)
    view.add_item(button_delete)
    
    await ctx.send(embed=embed, view=view)

@bot.command()
async def delete(ctx):
    if ctx.channel.name.startwith("ticket-"):
        await ctx.send("This ticket will be deleted in 3 seconds...")
        await asyncio.sleep(3)
        await ctx.channel.delete()
    else:
        await ctx.send("This command can be used only in a ticket.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def transcript(ctx):
    guild = ctx.guild
    transcript_channel_name = "transcripts"

    transcript_channel = discord.utils.get(guild.text_channels, name=transcript_channel_name)

    if transcript_channel is None:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        staff_role = discord.utils.get(guild.roles, name="Staff")
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        transcript_channel = await guild.create_text_channel(
            name=transcript_channel_name,
            overwrites=overwrites,
            reason="Transcript channel creation for tickets."
        )
        await ctx.send("Channel **transcripts** has been created!")

    if ctx.channel.name.startswith("ticket-"):
        await ctx.send("Generating transcript...")

        transcript_file = f"transcript-{ctx.channel.name}.txt"
        with open(transcript_file, "w", encoding="utf-8") as file:
            async for message in ctx.channel.history(limit=None, oldest_first=True):
                file.write(f"{message.created_at} - {message.author}: {message.content}\n")

        await transcript_channel.send(
            f"Transcript for {ctx.channel.mention} generated by {ctx.author.mention}:",
            file=discord.File(transcript_file)
        )
        await ctx.send("Transcript has been sent to the transcripts channel!")

    else:
        await ctx.send("This command can be used only in ticket.")

################################# v0.2 #################################

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Nu ai permisiunea de a folosi această comandă.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Folosește comanda corectă.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Comanda nu există.")
    else:
        await ctx.send(f"A apărut o eroare: {error}")
        raise error

TOKEN = 'YOUR_TOKEN'
create_db()
bot.run(TOKEN)