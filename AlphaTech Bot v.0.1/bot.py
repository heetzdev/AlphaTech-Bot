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
    print(f'✅ Botul {bot.user} este online!')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Nespecificat"):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} a fost banat. Motiv: {reason}")
    except Exception as e:
        await ctx.send(f"Nu am putut bana utilizatorul. Eroare: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member: discord.User, *, reason="Nespecificat"):
    try:
        await ctx.guild.unban(member)
        await ctx.send(f"{member.mention} a fost debanat. Motiv {reason}")
    except Exception as e:  
        await ctx.send(f"Nu am putut debana. Eroare: {e}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Nespecificat"):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} a fost kick-uit. Motiv: {reason}")
    except Exception as e:
        await ctx.send(f"Nu am putut kick-ui utilizatorul. Eroare: {e}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("Nu am permisiuni pentru a modifica roluri.")
        return
    
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role is None:
        mute_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
        
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(mute_role, send_messages=False)
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(mute_role, speak=False)
            
    if mute_role in member.roles:
        await ctx.send(f"{member} este deja pe mute.")
        return
    
    try:
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"{member} a fost pus pe mute: Motiv: {reason if reason else 'Fara Motiv'}")
    except discord.Forbidden:
        await ctx.send("Nu am pemisiuni pentru a pune acest utilizator pe mute")
    except discord.HTTPException:
        await ctx.send("a aparut o eroare la incercarea de a pune utilizatorul pe mute")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, time: int, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("❌ Nu am permisiuni pentru a modifica roluri.")
        return

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role is None:
        mute_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
        
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(mute_role, send_messages=False)
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(mute_role, speak=False)
    
    if mute_role in member.roles:
        await ctx.send(f"❌ {member} este deja pe mute.")
        return

    try:
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"✅ {member} a fost pus pe mute pentru {time} minute. Motiv: {reason if reason else 'Fără motiv.'}")

        await asyncio.sleep(time * 60)

        await member.remove_roles(mute_role)
        await ctx.send(f"✅ {member} nu mai este pe mute după {time} minute.")
        
    except discord.Forbidden:
        await ctx.send("❌ Nu am permisiuni suficiente pentru a pune acest utilizator pe mute.")
    except discord.HTTPException:
        await ctx.send("❌ A apărut o eroare la încercarea de a pune utilizatorul pe mute.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("Nu am permisiuni pentru a modifica roluri.")
        return
    
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role is None:
        await ctx.send("Rolul 'muted' nu exista pe server")
        return
    
    if mute_role not in member.roles:
        await ctx.send(f"{member} nu este pe mute")
        return
    
    try:
        await member.remove_roles(mute_role, reason=reason)
        await ctx.send(f"{member} a fost deblocat de pe mute. Motiv: {reason if reason else 'Fara Motiv.'}")
    except discord.Forbidden:
        await ctx.send("Nu am permisiuni suficiente pentru a dezactiva mute-ul acestui utilizator")
    except discord.HTTPException:
        await ctx.send("A aparut o eroare la incercarea de a dezactiva mute-ul acestui utilizator")

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = "Comenzi disponibile",
        description="Lista comenzilor pe care le poti folosi",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="!mute <@utilizator> [motiv]", value="Pune un utilizator pe mute pana dai unmute.", inline=False)
    embed.add_field(name="!unmute <@utilizator> [motiv]", value="Inlatura mute unui utilizator.", inline=False)
    embed.add_field(name="!tempmute <@utilizator> [motiv]", value="Pune un utilizator pe mute (temporar)", inline=False)
    embed.add_field(name="!ban <@utilizator> [motiv]", value="Baneaza un utilizator pe server", inline=False)
    embed.add_field(name="!unban <@utilizator> [motiv]", value="Debaneaza un utilizator", inline=False)
    embed.add_field(name="!purge <amount>", value="sterge un anumit numar de mesaj", inline=False)
    embed.add_field(name="!help", value="afiseaza lista comenzilor disponibile", inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1:
        await ctx.send("Trebuie sa specifici un numar mai mare decat 0", defete_after=5)
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"am sters {amount} mesaje!", delete_after=5)

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
        raise error  # Pentru debugging, vezi eroarea completă în consolă

TOKEN = 'YOUR_TOKEN'
bot.run(TOKEN)
