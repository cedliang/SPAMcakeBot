import discord
import random, sys
from discord.ext import commands


class Neil(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.neildict = None

    @commands.Cog.listener()
    async def on_ready():
        with open("loremflattened.txt", encoding='utf8') as f:
            readfile = f.read()
            self.neildict = makerule(data, 2)

    @commands.command()
    async def neil(self, ctx):
        wisetweet = makestring(rule, random.randint(15,35))
        await ctx.send(wisetweet)

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


        if oldwords[0] == '':
            pass

        else:

            if (ord(oldwords[0][0]) >= 65) and (ord(oldwords[0][0]) <= 90):
                validstart = True
            elif ord(oldwords[0][0]) >= 97 and ord(oldwords[0][0]) <= 122:
                validstart = True
                capitalise = True



    string = ' '.join(oldwords) + ' '

    for i in range(length):
        try:
            key = ' '.join(oldwords)
            newword = random.choice(rule[key])
            string += newword + ' '

            for word in range(len(oldwords)):
                oldwords[word] = oldwords[(word + 1) % len(oldwords)]
            oldwords[-1] = newword

        except KeyError:
            if capitalise:
                string = string[0].upper() + string[1:]

            lastperiodindex = string.rfind(".")
            if lastperiodindex == -1:
                return string[0:len(string)-1] + "."
            string = string[:lastperiodindex+1]


            return string
    if capitalise:
        string = string[0].upper() + string[1:]

    print(string + "\n")

    lastperiodindex = string.rfind(".")
    if lastperiodindex == -1:
        return string[0:len(string)-1] + "."
    string = string[:lastperiodindex+1]


    return string




def setup(client):
    client.add_cog(Neil(client))