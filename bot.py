"""

This is the official source code for the RPI RA Bot for Discord.

RA Bot is designed to suplement, not replace the duties of an
RA, it is primarily intended as a quick support source for residents.


"""

import discord
import os
import asyncio
from discord.ext import commands
import numpy as np
import random
import datetime


from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = '!')


"""
botHome is a global numpy ndArray of discord.textchannel objects.
The respective guild of the home channel is obtainable via
botHome[k].guild.
"""

async def checkSend(ctx,mCont,returnTF = False):
    msgSent= False
    for i in range(0,botHome.size):
        if botHome[i].guild == ctx.guild:
            await botHome[i].send(mCont)
            msgSent= True
            break
    if not msgSent:
        await ctx.send("Huh, it doesn't look like I'm set up on this server.\nMake sure to use botInit command first, and try again.")
    
    if returnTF:
        return msgSent
    
async def getRA(ctx):
    
    roleList = np.array([])
    
    if len(ctx.guild.roles) > 1:
        for i in ctx.guild.roles:
            roleList = np.append(roleList, np.array(i))
        
        roleString = "Please select the role which represents RAs in this server.\n"
        
        for i in range(1,roleList.size):
            roleString += f'{roleList[i].name}\n'
            
        await checkSend(ctx,roleString)
            
        def check(m):
            print(m.content)
            return m.author == ctx.author
        
        maxIter = 5
        totIter = 0
        notConfirmed = True
        
        while notConfirmed and totIter < maxIter:
            
            if totIter != 0:
                await checkSend(ctx, f"Looks like you may have made a mistake, try again.")
            
            totIter += 1
            
            raConfirm = await client.wait_for('message',check=check)
        
            for i in roleList:
                if i.name == raConfirm.content:
                    notConfirmed = False
                    return i
        
        if notConfirmed:
            await checkSend(ctx, "You've exceded your number of attempts, please restart the init process.")
    
    else:
        return roleList

@client.event
async def on_ready():
    print("Bot is Online")
    global botHome
    botHome = np.array([])
    
@client.command(hidden = True)
async def setHome(ctx):
    global botHome
    if ctx.channel == ctx.guild.channels[0]:
        await ctx.send("Please don't use me in general channel.")
    else:
        existCheck = False
        for i in botHome:
            if i.guild == ctx.guild:
                i = ctx.channel
                existCheck = True
                await i.checkSend(ctx,f'My home on {i.guild.name} is {i.name}')
                break
        if not existCheck:
            botHome = np.append(botHome, np.array([ctx.channel]))
            await checkSend(botHome[-1],f'My home on {botHome[-1].guild.name} is {botHome[-1].name}')
    
    return botHome
    #print(f'The data type of {homeGuild} is {type(homeGuild)}')
    #print(homeGuild.roles)
    
@client.command()
async def initBot(ctx):
    await setHome(ctx)
    
    global raRole
    raRole = await getRA(ctx)
    
    
    
    await checkSend(ctx,"Perfect, I'm all set up on this server. If you want to change my home you can use the setHome command.\nIf I ever go off line, you'll need to use the init command again.")


def stringCheck(string,check):
    setReturn = -1
    for i in range(0,len(check)):
        if string.find(check[i]) != -1:
            setReturn = i
            break
    
    return setReturn

def raOnline(theGuild):
    
    sendBack = []
    
    for i in theGuild.roles[-1].members:
        if str(i.status) == "online":
            sendBack.append(i)
            
    return sendBack

def checkCommand(message):
    if message.content[0] == '!':
        return True
    else:
        return False

async def checkFix(string):
    fixKeys = ['fixx','Fixx','fix','Fix',
               'broken', 'damaged', 'leak', 
               'leaky']
    if stringCheck(string.content,fixKeys) != -1:
        fixString = ''
        fixString += f"Hey I noticed you mentioned {fixKeys[stringCheck(string.content,fixKeys)]}\n"
        raList = raOnline(string.guild)
        if raList != []:
            raString = raList[0].nick
            if len(raList) > 2:
                for i in range(1,len(raList)-1):
                    raString += f", {raList[i].nick}"
                raString += f", and {raList[-1].nick}"
            raString += " can help you more, but I'll provide some resources right now.\n"
        else:
            raString += "It doesn't look like ther are any RA's online to help you right now.\n Let me provide some resources.\n"
        
        fixString += raString
        
        fixString += "RPI's FIXX department can be reached in several ways:\n"
        fixString += "Ph: 518-276-2000 (business hours only)\nEmail: fixx@rpi.edu \n"
        fixString += "If it's an after hours emergency, call Pub Safe at 518-276-6479"
        
        await checkSend(string,fixString)
        
async def checkDotCio(string):
    dotCioKeys = ["can't connect", "trouble connecting",
                  "Can't connect", "Trouble connecting"]
    if stringCheck(string.content,dotCioKeys) != -1:
        dotCioString = ''
        dotCioString += f"Hey I noticed you mentioned {dotCioKeys[stringCheck(string,dotCioKeys)]}\n"
        raList = raOnline(string.guild)
        if raList != []:
            raString = raList[0].nick
            if len(raList) > 2:
                for i in range(1,len(raList)-1):
                    raString += f", {raList[i].nick}"
                raString += f", and {raList[-1].nick}"
            raString += " can help you more, but I'll provide some resources right now.\n"
        else:
            raString += "It doesn't look like ther are any RA's online to help you right now.\n Let me provide some resources.\n"
        
        dotCioString += raString
        
        dotCioString += "RPI's student help desk can be reached in several ways:\n"
        dotCioString += "Ph: 518-276-7777 (business hours only)\nWeb address: https://dotcio.rpi.edu/support/helpdesk\n"
        dotCioString += "Don't forget to ask your peers, they may have dealt with this problem before."
        
        await checkSend(string,dotCioString)
        
    
@client.event
async def on_message(message):
    print(f"{message.author} sent a message")
    if message.author.bot != True and not checkCommand(message):
        initCheck = False
        lastBotMsg = datetime.datetime.min
        for i in message.guild.channels:
            try:
                lastBotMsgTemp =await i.history().get(author__name='RA Bot')
                if lastBotMsg < lastBotMsgTemp:
                    lastBotMsg = lastBotMsgTemp
            except:
                blankVal = 1
                
        timeDiff = message.created_at - lastBotMsg
        for i in botHome:
            if message.guild == i.guild:
                initCheck = True
                break
        if initCheck:
            await checkFix(message)
            await checkDotCio(message)
        elif timeDiff.seconds > 10 :
            await message.channel.send("Huh, looks like I haven't been set up on this server yet. You can do that using the initBot command.")
        else:
            print(f'{message.author} is trying to spam the bot on {message.channel}-{message.guild}')
        
    
    await client.process_commands(message)

        
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong \n{round(client.latency*1000)}ms')
    
@client.command()
async def pong(ctx):
    await ctx.send(f'You fool, you absolute buffoon. How could you be such a simpleton. \n You have no place at my table.')
    
@client.command(aliases=['Oh'])
async def _8ball(ctx, question):
    if ctx.message.author.name == "Clyde":
        await ctx.send("The gods smile upon your endeavors")
    elif ctx.message.author.name == "Vanessa":
        await ctx.send("Doubtful")
#    elif ctx.message.author.role.is_default():
#        ctx.send("Perhaps")
    else:
        await ctx.send("Concentrate harder and ask again")
    
@client.command(hidden = True)
async def leave(ctx):
    await ctx.send("Heading out")
    await client.close()
    
@client.command(hidden = True)
async def debug(ctx,*,deliverable):
    await checkSend(ctx,deliverable)
    
@client.command()
async def allowance(ctx):
    rng = random.random()
    if rng < 0.9:
        await checkSend(ctx, f"{ctx.nick} has collected their daily allowance of 100 points.")
    
    else:
        await checkSend(ctx, f"{ctx.nick} has recieved an extra large allowance of 200 points.")

    
#await client.start(TOKEN)
