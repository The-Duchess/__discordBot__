from .mpbot import ManagedPluginBot, methodcommand
import discord
import discord.ext.commands as commands
import functools as ft
import re #eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
from config import CONFIG as conf

# state tracking tools
import fileinput
import sys
import shelve

def is_owner(func):
    @ft.wraps(func)
    async def decorated(self, ctx, *args, **kwargs):
        if await ctx.bot.is_owner(ctx.author):
            return await func(self, ctx, *args, **kwargs)
        else:
            await ctx.channel.send('you are not the owner')

    return decorated

def is_admin(func):
    @ft.wraps(func)
    async def decorated(self, ctx, *args, **kwargs):
        if ctx.message.author.id in conf['ADMIN_LIST']:
            return await func(self, ctx, *args, **kwargs)
        else:
            await ctx.channel.send('you are not an admin')

    return decorated

class MyBot(ManagedPluginBot):

    async def on_ready(self):
        print('------------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------------')

    @methodcommand() #TODO: add logic to check permission
    @is_owner
    async def terminate(self, ctx):
        print('Shutting down...')
        await self.logout()

    @methodcommand()
    @is_owner
    @is_admin
    async def reset_warnings(self, ctx, user: discord.User):
        try:
            state_db = shelve.open(conf['STATE_FILE'], writeback=True)
            state_db['warn_list'][user.id]['warnings'] = []
            state_db['warn_list'][user.id]['times'] = 0

            # state_db.sync()
            state_db.close()
        except:
            pass

    @methodcommand()
    @is_admin
    async def warn(self, ctx, user : discord.User, *arg : str):

        # the bot cannot be warned
        if user.id == conf['BOTID']:
            return

        reason = ' '.join(arg)
        # warn_list :
        #   id : {
        #           warnings : [],
        #           times    : n
        #       }

        state_db = shelve.open(conf['STATE_FILE'], writeback=True)
        if 'warn_list' in state_db:
            if user.id in state_db['warn_list']:
                state_db['warn_list'][user.id]['warnings'].append(f'{reason}:{ctx.author.name}')
                state_db['warn_list'][user.id]['times'] += 1
            else:
                state_db['warn_list'][user.id] = {
                                                    'warnings' : [reason],
                                                    'times'    : 1
                                                 }
        else:
            state_db['warn_list'] = {
                                    user.id : {
                                                'warnings' : [reason],
                                                'times'    : 1
                                              }

                                    }

        warning_num = state_db['warn_list'][user.id]['times']

        await ctx.channel.send(f'{user.mention} you have been warned for: {reason}. you have {warning_num} warnings. further warnings may constitute a ban')

        if state_db['warn_list'][user.id]['times'] >= conf['WARN_CAP']:
            name = user.name
            await ctx.guild.ban(user, reason="too many warnings", delete_message_days=1)
            await ctx.channel.send(f'{name} was banned for being warned too many times')

        # state_db.sync() # not sure if necessary
        state_db.close()

    @methodcommand()
    @is_admin
    async def warnings(self, ctx, user: discord.User):
        state_db = shelve.open(conf['STATE_FILE'], writeback=False)
        try:
            warning_num = state_db['warn_list'][user.id]['times']
            cap = conf['WARN_CAP']
            await ctx.channel.send(f'{user.mention} has {warning_num} warnings. reminder {cap} warnings results in an automatic ban.')
            await ctx.author.send(f'{user.mention} has {warning_num} warnings. reminder {cap} warnings results in an automatic ban.')
            for warn in state_db['warn_list'][user.id]['warnings']:
                await ctx.author.send(warn)
                sleep(0.2)
        except:
            ctx.channel.send('f{user.name} has no warnings')

        state_db.close()

    @methodcommand()
    @is_admin
    async def ban(self, ctx, user : discord.User, *arg : str):

        # the bot cannot be banned
        if user.id == conf['BOTID']:
            return

        reason = ' '.join(arg)
        name = user.name
        await ctx.guild.ban(user, reason=reason, delete_message_days=0)
        await ctx.channel.send(f'{name} banned by {ctx.message.author.name} for: {reason}')

    @methodcommand()
    @is_admin
    async def mute(self, ctx, user : discord.Member, *arg : str):
        role = discord.utils.get(user.guild.roles, name='mute')
        reason = ' '.join(arg)
        await user.add_roles(role, reason=reason, atomic=True)
        await ctx.channel.send(f'{user.mention} was muted by {ctx.message.author.name} for: {reason}')

    @methodcommand()
    @is_admin
    async def unmute(self, ctx, user : discord.Member, *arg : str):
        role = discord.utils.get(user.guild.roles, name='mute')
        reason = ' '.join(arg)
        await user.remove_roles(role, reason=reason, atomic=True)
        await ctx.channel.send(f'{user.mention} was unmuted by {ctx.message.author.name} for: {reason}')
