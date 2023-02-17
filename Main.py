import discord
from discord.ext import commands
from collections import defaultdict
import asyncio
import requests
import random


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

warn_count = defaultdict(int)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command(name='clear', help='Clears messages in a channel. Usage: !clear <number of messages>')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

@client.command(name='mute', help='Mutes a user. Usage: !mute <user> <reason>')
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    for role in guild.roles:
        if role.name == 'Muted':
            await member.add_roles(role)
            await ctx.send(f'{member.mention} has been muted for {reason}.')
            return
    overwrite = discord.PermissionOverwrite(send_messages=False)
    new_role = await guild.create_role(name='Muted')
    for channel in guild.text_channels:
        await channel.set_permissions(new_role, overwrite=overwrite)
    await member.add_roles(new_role)
    await ctx.send(f'{member.mention} has been muted for {reason}.')

@client.command(name='ban', help='Bans a user. Usage: !ban <user> <reason>')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned for {reason}.')

@client.command(name='timeout', help='Timeouts a user. Usage: !timeout <user> <reason>')
@commands.has_permissions(kick_members=True)
async def timeout(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    for role in guild.roles:
        if role.name == 'Timeout':
            await member.add_roles(role)
            await ctx.send(f'{member.mention} has been timed out for {reason}.')
            return
    overwrite = discord.PermissionOverwrite(send_messages=False)
    new_role = await guild.create_role(name='Timeout')
    for channel in guild.text_channels:
        await channel.set_permissions(new_role, overwrite=overwrite)
    await member.add_roles(new_role)
    await ctx.send(f'{member.mention} has been timed out for {reason}.')

@client.command(name='kick', help='Kicks a user. Usage: !kick <user> <reason>')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked for {reason}.')

@client.command(name='warn', help='Warns a user. Usage: !warn <user> <reason>')
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    # Increment the number of times the user has been warned
    warn_count[member.id] += 1
    
    # If the user has been warned 3 times, mute the user for 10 minutes
    if warn_count[member.id] == 3:
        guild = ctx.guild
        for role in guild.roles:
            if role.name == 'Muted':
                await member.add_roles(role)
                await ctx.send(f'{member.mention} has been muted for 10 minutes due to too many warnings.')
                # Remove the muted role after 10 minutes
                await asyncio.sleep(600)
                await member.remove_roles(role)
                await ctx.send(f'{member.mention} has been unmuted.')
                return
        overwrite = discord.PermissionOverwrite(send_messages=False)
        new_role = await guild.create_role(name='Muted')
        for channel in guild.text_channels:
            await channel.set_permissions(new_role, overwrite=overwrite)
        await member.add_roles(new_role)
        await ctx.send(f'{member.mention} has been muted for 10 minutes due to too many warnings.')
        # Remove the muted role after 10 minutes
        await asyncio.sleep(600)
        await member.remove_roles(new_role)
        await ctx.send(f'{member.mention} has been unmuted.')
    else:
        await ctx.send(f'{member.mention} has been warned for {reason}. This is warning number {warn_count[member.id]}.')

@client.command(name='meme', help='Sends a coding or cybersecurity meme')
async def meme(ctx):
    # List of subreddits to get memes from
    subreddits = ['ProgrammerHumor', 'CodingMemes', 'netsecmemes']
    # Choose a random subreddit from the list
    subreddit = random.choice(subreddits)
    # Make a request to the subreddit's API to get a random post
    response = requests.get(f'https://www.reddit.com/r/{subreddit}/random.json', headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        # Get the post data from the JSON response
        post_data = response.json()[0]['data']['children'][0]['data']
        # If the post is a link to an image, send the image to the channel
        if 'url_overridden_by_dest' in post_data and post_data['url_overridden_by_dest'].endswith(('.png', '.jpg', '.jpeg')):
            await ctx.send(post_data['url_overridden_by_dest'])
        # If the post is a text post, send the post's title and selftext to the channel
        else:
            await ctx.send(f'{post_data["title"]}\n{post_data["selftext"]}')
    else:
        await ctx.send('Failed to get meme :(')


@client.command(name='help', help='Displays this help message')
async def help(ctx, command=None):
    if command is None:
        # Display help message for all commands
        embed = discord.Embed(title='Help', description='List of available commands:', color=discord.Color.blue())
        for cmd in client.commands:
            embed.add_field(name=cmd.name, value=cmd.help, inline=False)
        await ctx.send(embed=embed)
    else:
        # Display help message for a specific command
        cmd = client.get_command(command)
        if cmd is None:
            await ctx.send(f'Command "{command}" not found')
        else:
            embed = discord.Embed(title=cmd.name, description=cmd.help, color=discord.Color.blue())
            await ctx.send(embed=embed)


client.run('ur_token')