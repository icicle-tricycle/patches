# A discord bot that responds to user input
# Created by Peter McNamara

# To use discord at all
import discord
# for random numbers
import random
# for files
import json
# for files and file io
import os

# for requesting from APIs
import requests
# for time, and converting unix time to human readable time
import datetime
# for timezones, using "timezone"
import pytz

print('Bot intializing')
client = discord.Client()

# A list of all the simple call/response commands, in lower case
simpleCommandsDict = {
    'Azorius': 'White Blue',
    'Izzet': 'Blue Red`',
    'Rakdos': 'Black Red',
    'Golgari': 'Black Green',
    'Selesyna': 'Green White',
    'Boros': 'Red White',
    'Orzhov': 'White Black',
    'Dimir': 'Blue Black',
    'Simic': 'Green Blue',
    'Gruul': 'Red Green',

    'Bant': 'Green **White** Blue',
    'Esper': 'White **Blue** Black',
    'Grixis': 'Blue **Black** Red',
    'Jund': 'Black **Red** Green',
    'Naya': 'Red **Green** White',

    'Abzan': '**White** Black Green',
    'Jeskai': '**Blue** Red White',
    'Sultai': '**Black** Green Blue',
    'Mardu': '**Red** White Black',
    'Temur': '**Green** Blue Red'
}
simpleCommandsDict = {k.lower(): v for k, v in simpleCommandsDict.items()}


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        # if I sent the message, leave the event
        print('I just saw my own message')
        return
    messageLower = message.content.lower()
    print('Message recieved: ' + message.content)
    print('Author ID: ' + message.author.id)

    for textCommand in simpleCommandsDict:
        if messageLower.startswith('!' + textCommand):
            print('Responded to simple call/response command: !' + textCommand)
            await client.send_message(message.channel, responseString(textCommand))
            break
    # if message.content.startswith('!flipcoin'):
    if messageLower.startswith('!flipcoin'):
        await client.send_message(message.channel, flipCoin())
    elif messageLower.startswith('!rolldie'):
        input = message.content[8:]
        output = rollDie(input)
        await client.send_message(message.channel, output)
    elif messageLower.startswith('!addquote'):
        feedback = addQuote(message)
        if feedback == 'finished':
            await client.send_message(message.channel, 'Added quote')
    elif messageLower.startswith('!quote'):
        quote = returnQuote(message.channel)
        if(quote == 'error'):
            await client.send_message(message.channel, 'No quotes found, use !addquote <quote here> to add a quote!')
        else:
            await client.send_message(message.channel, quote)
    elif messageLower.startswith('!countchannel'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        # counter = countChannel(client)
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        responseText = 'You\'ve sent {} messages in the past 100 here. (including this response)'
        await client.edit_message(tmp, responseText .format(counter))
    elif (messageLower.startswith('!iss') or messageLower.startswith('!spacestation')):
        await client.send_message(message.channel,  issLocation())

# This is where all the commands' code is. Honestly this might be better in a separate file


def responseString(input):
    # for simple call/response commands
    return simpleCommandsDict.get(input, 'Error, invalid input')
    # Get looks for a key of the value of input, and defaults to the 2nd string


def flipCoin():
    # randomly return heads or tails
    flip = random.choice(['Heads', 'Tails'])
    return flip


def rollDie(sides):
    # return a random number between 1 and N
    print('Entered rolldie function with sides: ' + sides)
    try:
        output = random.randint(1, int(sides))
        return output
    except TypeError:
        # unless the input doesn't work, possibly because it isn't an integer
        return "Invalid input"
    except ValueError:
        # unless the input doesn't work, because it's an invalid value (like a negative number)
        return 'Invalid value'
    except:
        # unless some other unforeseeable act of god says no
        return "Error"


def countMessages(client):
    # count all the messages in the channel, with a maximum cutoff
    # I need to review async programming and coroutines before migrating this code
    counter = 0
    # async for log in client.logs_from(message.channel, limit=100):
    #     if log.author == message.author:
    #        counter += 1
    return counter


def addQuote(message):
    #
    print('About to add quote')
    if not os.path.isfile("quote_file.json"):
        quote_list = []
        print('File made')
    else:
        with open("quote_file.json", "r") as quote_file:
            quote_list = json.load(quote_file)
        print('File loaded')
    quote_list.append(message.content[9:])  # Skip the '!addquote'
    with open("quote_file.json", "w") as quote_file:
        json.dump(quote_list, quote_file)
    return 'finished'


def returnQuote(channel):
    # Return a quote from the file
    if not os.path.isfile("quote_file.json"):
        quote_list = []
        output = 'error'
    else:
        with open("quote_file.json", "r") as quote_file:
            quote_list = json.load(quote_file)
            output = random.choice(quote_list)
    return output


def issLocation():
    # Use open-notify to request the current ISS location
    # Documentation: http://open-notify.org/Open-Notify-API/ISS-Location-Now/
    output = 'Error, International Space Station not found.'
    response = requests.get("http://api.open-notify.org/iss-now.json")
    # It's probably bad practice to just trust the json, TODO: fix this
    print('Status code: ' + str(response.status_code))
    data = response.json()
    if response.status_code == 200:
        outLat = data['iss_position']['latitude']
        outLong = data['iss_position']['longitude']
        updateTime = datetime.datetime.fromtimestamp(data['timestamp'])  # In time local to machine
        updateTime = pytz.timezone('US/Eastern').localize(updateTime)
        # currentTime = datetime.datetime.now()  # local time
        # currentTime = datetime.datetime.utcnow()  # UTC time
        # currentTime = datetime.datetime.now(datetime.timezone.utc)  # UTC timezone time
        # updateTime = updateTime.replace(tzinfo=None)
        # replace(tzinfo=None)
        # outTimeSinceUpdate = (currentTime - updateTime)
        # days, hours, minutes = daysHoursMinutes(outTimeSinceUpdate)
        # outTimeSinceUpdate =\
        #     str(days) + ' days, ' +\
        #     str(hours) + ' hours and, ' +\
        #     str(minutes) + ' minutes ago.'
        # It's probably also bad practice to just trust that lat/long are numbers. TODO: check for valid data type
        if float(outLat) > 0:
            outLat += 'N'
        else:
            outLat = outLat[1:]
            outLat += 'S'
        if float(outLong) > 0:
            outLong += 'E'
        else:
            outLong = outLong[1:]
            outLong += 'W'
        output = \
            'The International Space Station is at ' + \
            outLat + ', ' + outLong + '\n' +\
            'Last updated at: ' + timeToString(updateTime)  # + ' US/Eastern\n'  # +\
        #    'Current time: ' + timeToString(currentTime) + ' Eastern\n'  # +\
        #   'Which was ' + outTimeSinceUpdate
    return output


def daysHoursMinutes(time_delta):
    # Convert a time_delta into days, hours, and minutes
    return time_delta.days, time_delta.seconds // 3600, time_delta.seconds % 3600 // 60


def timeToString(datetime):
    # format a datetime to a string
    return datetime.strftime('%Y-%m-%d %H:%M:%S %Z%z')


def hsCardLookup(name):
    # A search by name of all collectible cards, returns all related results
    response = unirest.get(
        "https://omgvamp-hearthstone-v1.p.mashape.com/cards/search/" + name + "?collectible=1",
        headers={
            "X-Mashape-Key": "sR83ncojSVmshWb0ulVcvyTDaLpxp15JWzdjsnP9644BnkoBgh",
            "X-Mashape-Host": "omgvamp-hearthstone-v1.p.mashape.com"
        }
    )

    return 'No Card Found'


def hsSpecificCardLookup(name):
    # A search by name of all collectible cards, returns 1 card
    response = unirest.get(
        "https://omgvamp-hearthstone-v1.p.mashape.com/cards/" + name + "?collectible=1",
        headers={
            "X-Mashape-Key": "sR83ncojSVmshWb0ulVcvyTDaLpxp15JWzdjsnP9644BnkoBgh",
            "X-Mashape-Host": "omgvamp-hearthstone-v1.p.mashape.com"
        }
    )

    return 'No Card Found'


# Actually run the program, using my discord's bot user token
client.run('MzYxOTQ3NjI3Njk4NTIwMDc1.DKrpcQ.QI8RblrilYpAYwfQiO7qPxemF9Q')
