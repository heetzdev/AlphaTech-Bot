# create by heetz for AlphaTech
# v 0.1

import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Unspecified"):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"Could not ban the user. Error: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member: discord.User, *, reason="Unspecified"):
    try:
        await ctx.guild.unban(member)
        await ctx.send(f"{member.mention} has been unbanned. Reason: {reason}")
    except Exception as e:  
        await ctx.send(f"Could not unban. Error: {e}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Unspecified"):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"Could not kick the user. Error: {e}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I don't have permission to modify roles.")
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
        await ctx.send(f"{member} has been muted: Reason: {reason if reason else 'No Reason'}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to mute this user.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to mute the user.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, time: int, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I don't have permission to modify roles.")
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
        await ctx.send(f"{member} is no longer muted after {time} minutes.")
        
    except discord.Forbidden:
        await ctx.send("I don't have sufficient permissions to mute this user.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to mute the user.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I don't have permission to modify roles.")
        return
    
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role is None:
        await ctx.send("The 'Muted' role does not exist on the server.")
        return
    
    if mute_role not in member.roles:
        await ctx.send(f"{member} is not muted.")
        return
    
    try:
        await member.remove_roles(mute_role, reason=reason)
        await ctx.send(f"{member} has been unmuted. Reason: {reason if reason else 'No Reason.'}")
    except discord.Forbidden:
        await ctx.send("I don't have sufficient permissions to unmute this user.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to unmute this user.")

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = "Available Commands",
        description="List of commands you can use",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="!mute <@user> [reason]", value="Mute a user until unmuted.", inline=False)
    embed.add_field(name="!unmute <@user> [reason]", value="Unmute a user.", inline=False)
    embed.add_field(name="!tempmute <@user> [reason]", value="Temporarily mute a user.", inline=False)
    embed.add_field(name="!ban <@user> [reason]", value="Ban a user from the server.", inline=False)
    embed.add_field(name="!unban <@user> [reason]", value="Unban a user.", inline=False)
    embed.add_field(name="!purge <amount>", value="Delete a specific number of messages.", inline=False)
    embed.add_field(name="!help", value="Displays the list of available commands.", inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1:
        await ctx.send("You must specify a number greater than 0", delete_after=5)
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"I deleted {amount} messages!", delete_after=5)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please use the correct command format.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        await ctx.send(f"An error occurred: {error}")
        raise error

TOKEN = 'YOUR_TOKEN'
bot.run(TOKEN)
