from config import CONFIG

def runBot(keyList):
    from mybot import MyBot
    myBot = MyBot(plugins_dir='plugins', config_file='config',command_prefix='.')
    myBot.run(keyList['DISCORDAPPKEY'])

runBot(CONFIG)
