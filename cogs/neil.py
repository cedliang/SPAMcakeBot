import discord
import random, sys
from discord.ext import commands
from datetime import datetime, timedelta

class Neil(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.neildict = None

    @commands.command()
    async def neil(self, ctx):
        if self.neildict is None:
            with open("loremfinal.txt", encoding='utf8') as f:
                readfile = f.read()
                self.neildict = makerule(readfile, 2)
        wisetweet = makestring(self.neildict, random.randint(15,35))

        timenow = datetime.now()
        timenowstring = timenow.strftime("%b %d")
        neilEmbed = discord.Embed(title = 'Neil deGrasse Tyson', description = None, color = discord.Colour.from_rgb(29, 161, 242))
        neilEmbed.add_field(name = f'@neiltyson\t\t{timenowstring}', value = wisetweet, inline = True)
        neilEmbed.set_thumbnail(url="https://pbs.twimg.com/profile_images/74188698/NeilTysonOriginsA-Crop_400x400.jpg")

        await ctx.send(embed = neilEmbed)

def makerule(data, context):
    '''Make a rule dict for given data.'''
    rule = {}
    words = data.split(' ')
    index = context
    for word in words[index:]:
        key = ' '.join(words[index-context:index])
        if key in rule:
            rule[key].append(word)
        else:
            rule[key] = [word]
        index += 1
    return rule

def makestring(rule, length):
    '''Use a given rule to make a string.'''
    validstart = False
    capitalise = False

    while not validstart:
        oldwords = random.choice(list(rule.keys())).split(' ') #random starting words
        if oldwords[0] != '':
            if (ord(oldwords[0][0]) >= 65) and (ord(oldwords[0][0]) <= 90):
                validstart = True
            elif ord(oldwords[0][0]) >= 97 and ord(oldwords[0][0]) <= 122:
                validstart = True
                capitalise = True

    string = ' '.join(oldwords) + ' '

    for _ in range(length):
        try:
            key = ' '.join(oldwords)
            newword = random.choice(rule[key])
            string += f'{newword} '
            for word in range(len(oldwords)):
                oldwords[word] = oldwords[(word + 1) % len(oldwords)]
            oldwords[-1] = newword
        except KeyError:
            if capitalise:
                string = string[0].upper() + string[1:]

            lastperiodindex = string.rfind(".")
            if lastperiodindex == -1:
                return string[:-1] + "."
            string = string[:lastperiodindex+1]
            return string

    if capitalise:
        string = string[0].upper() + string[1:]
    lastperiodindex = string.rfind(".")
    if lastperiodindex == -1:
        return string[:-1] + "."
    string = string[:lastperiodindex+1]
    return string

def setup(client):
    client.add_cog(Neil(client))
