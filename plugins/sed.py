import discord.ext.commands as commands
from .template import PluginClass

import re

class SedSearchReplace(PluginClass):
    CONFIG_REQUIRED = False
    STORAGE_REQUIRED = False
    PATTERN_INPUT = re.compile(r'(?P<find>.+)\|(?P<replace>.+)\|(?P<tags>\w+)?')
    PATTERN_INPUT_NO_CASE = re.compile(r'(?P<find>.+)\|(?P<replace>.+)\|(?P<tags>\w+)?', re.IGNORECASE)

    def __unload(self):
        pass

    def __init__(self):
        pass

    def help():
        result = f'''
                ```
                Sed style search replace
                - usage: .sed <search regex>|replace string|args
                ```
                '''

        return tw.dedent(result)

    @commands.command(name='sed', aliases=['s'])
    async def sed(self, ctx, *args : str):
        """sed style search replace"""
        argsStr = ' '.join(args)
        match = SedSearchReplace.PATTERN_INPUT.fullmatch(argsStr)
        match_no_case = SedSearchReplace.PATTERN_INPUT_NO_CASE.fullmatch(argsStr)
        if match:
            async for m in ctx.channel.history():
                if m.author == ctx.bot.user or m.id == ctx.message.id:
                    continue

                original = m.content
                print(match.groups())
                find, replace, tags = match.groups()
                flags = 0
                count = 1
                if tags is not None:
                    if 'e' in tags:
                        # execute is currently disabled because it's dangerous
                        #replace = eval(f'lambda m: {replace}')
                        pass
                    if 'g' in tags:
                        flags = 0
                        count = 0
                    if 'i' in tags:
                        flags |= re.IGNORECASE

                new = re.sub(find, replace, original, count, flags)

                if new != original:
                    await ctx.send(f'{ctx.message.author.mention} meant: {new}')
                    break
        else:
            return
