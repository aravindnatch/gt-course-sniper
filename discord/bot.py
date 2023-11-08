import discord
import os
import time
import json
import peewee
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
term = os.getenv('term')
token = os.getenv('token')

client = discord.Client()

db = peewee.SqliteDatabase('../db/main.sqlite', pragmas={'journal_mode': 'wal', 'synchronous': 'full'})
class Classes(peewee.Model):
  crn=peewee.CharField(unique=True)
  status=peewee.CharField()
  userid=peewee.CharField()
  name=peewee.CharField()
  class Meta:
    database=db
    db_table='Classes'

db.create_tables([Classes])

db2 = peewee.SqliteDatabase('../db/waitlist.sqlite', pragmas={'journal_mode': 'wal', 'synchronous': 'full'})
class WaitlistClasses(peewee.Model):
   crn=peewee.CharField(unique=True)
   status=peewee.CharField()
   userid=peewee.CharField()
   name=peewee.CharField()
   class Meta:
      database=db2
      db_table='WaitlistClasses'

db2.create_tables([WaitlistClasses])

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
}

base_url = 'https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/searchResults/getClassDetails'

@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  args = message.content.split()

  if message.channel.id == 1008499401771196427 or message.author.id == 786106653497622528 or message.author.id == 398935841444986880:
    if args[0] == '!add':
      if len(args) == 2:
        try:
          req = requests.get(f"{base_url}?term={term}&courseReferenceNumber={str(args[1])}", headers=headers, timeout=5)
          soup = BeautifulSoup(req.text, 'html.parser')
          if req.status_code == 200:
            try:
              name = soup.find('span', string="Title:").find_next('span').text.strip()
              crn = soup.find('span', string="CRN:").find_next('span').text.strip()
              subject = soup.find('span', string="Subject:").find_next('span').text.strip()
              courseNumber = soup.find('span', string="Course Number:").find_next('span').text.strip()
              section = soup.find('span', string="Section Number:").find_next('span').text.strip()
              title = f"{name} - {crn} - {subject} {courseNumber} - {section}"

              try:
                userlist = json.dumps([str(message.author.id)])
                rec1=Classes(crn=args[1],status='open',userid=userlist,name=title)
                rec1.save()
                await message.channel.send('Added: ' + title)
              except Exception as e:
                if type(e). __name__ == "IntegrityError":
                  obj=Classes.get(Classes.crn==args[1])
                  users = json.loads(obj.userid)
                  newuser = str(message.author.id)

                  if newuser not in users:
                    users.append(newuser)
                    obj.userid = json.dumps(users)
                    obj.save()
                    await message.channel.send('Added: ' + title)
                  else:
                    await message.channel.send('You already added this crn')
                else:
                  print(str(e))
                  print("something went wrong")
            except Exception as e:
              await message.channel.send("crn does not exist")
          else:
            await message.channel.send("something went wrong while connecting to oscar, check your CRN try again")
        except Exception as e:
          print(str(e))
          await message.channel.send("something went wrong")
      else:
        await message.channel.send("invalid syntax")
    elif args[0] == '!remove':
      if len(args) == 2:
        fakeuser = str(message.author.id)
        try:
          obj=Classes.get(Classes.crn==str(args[1]))
          courseTitle = obj.name
          users = json.loads(obj.userid)
          if fakeuser in users:
            if len(users) == 1:
              obj.delete_instance()
              await message.channel.send('Removed: ' + courseTitle)
            else:
              users.remove(fakeuser)
              obj.userid = json.dumps(users)
              obj.save()
              await message.channel.send('Removed: ' + courseTitle)
          else:
            await message.channel.send('You havent added this crn yet')
        except Exception as e:
          await message.channel.send(str(e))
          await message.channel.send('You havent added this crn yet')
      else:
        await message.channel.send("invalid usage")
    elif args[0] == '!waitlistadd':
      if len(args) == 2:
        try:
          req = requests.get(f"{base_url}?term={term}&courseReferenceNumber={str(args[1])}", headers=headers, timeout=5)
          soup = BeautifulSoup(req.text, 'html.parser')
          if req.status_code == 200:
            try:
              name = soup.find('span', string="Title:").find_next('span').text.strip()
              crn = soup.find('span', string="CRN:").find_next('span').text.strip()
              subject = soup.find('span', string="Subject:").find_next('span').text.strip()
              courseNumber = soup.find('span', string="Course Number:").find_next('span').text.strip()
              section = soup.find('span', string="Section Number:").find_next('span').text.strip()
              title = f"{name} - {crn} - {subject} {courseNumber} - {section}"

              try:
                userlist = json.dumps([str(message.author.id)])
                rec1=WaitlistClasses(crn=args[1],status='open',userid=userlist,name=title)
                rec1.save()
                await message.channel.send('Added Waitlist: ' + title)
              except Exception as e:
                if type(e). __name__ == "IntegrityError":
                  obj=WaitlistClasses.get(WaitlistClasses.crn==args[1])
                  users = json.loads(obj.userid)
                  newuser = str(message.author.id)

                  if newuser not in users:
                    users.append(newuser)
                    obj.userid = json.dumps(users)
                    obj.save()
                    await message.channel.send('Added Waitlist: ' + title)
                  else:
                    await message.channel.send('You already added this crn')
                else:
                  print(str(e))
                  print("something went wrong")
            except Exception as e:
              await message.channel.send("crn does not exist")
          else:
            await message.channel.send("something went wrong while connecting to oscar, check your CRN try again")
        except Exception as e:
          print(str(e))
          await message.channel.send("something went wrong")
      else:
        await message.channel.send("invalid syntax")
    elif args[0] == '!waitlistremove':
      if len(args) == 2:
        fakeuser = str(message.author.id)
        try:
          obj=WaitlistClasses.get(WaitlistClasses.crn==str(args[1]))
          courseTitle = obj.name
          users = json.loads(obj.userid)
          if fakeuser in users:
            if len(users) == 1:
              obj.delete_instance()
              await message.channel.send('Waitlist Removed: ' + courseTitle)
            else:
              users.remove(fakeuser)
              obj.userid = json.dumps(users)
              obj.save()
              await message.channel.send('Waitlist Removed: ' + courseTitle)
          else:
            await message.channel.send('You havent added this crn yet')
        except Exception as e:
          await message.channel.send(str(e))
          await message.channel.send('You havent added this crn yet')
      else:
        await message.channel.send("invalid usage")
    elif args[0] == '!list':
      crns = Classes.select()
      waitcrns = WaitlistClasses.select()

      returnstr = '**Normal Registration:**\n'

      for x in crns:
        regd = json.loads(x.userid)
        if str(message.author.id) in regd:
          returnstr += f"{x.name}\n"

      returnstr += '\n**Waitlist Registration:**\n'

      for x in waitcrns:
        regd = json.loads(x.userid)
        if str(message.author.id) in regd:
          returnstr += f"{x.name}\n"

      await message.channel.send(str(returnstr).strip())
    elif args[0] == '!listall':
      crns = Classes.select()
      waitcrns = WaitlistClasses.select()
      returnstr = ""

      returnstr += '\nmain\n'

      crnlist = []
      for x in crns:
        regd = json.loads(x.userid)
        crnlist.append(str(x.crn) + str(regd))

      returnstr += '\n'.join(crnlist)
      returnstr += '\n\nwaitlist\n'

      waitcrnlist = []
      for x in waitcrns:
        regd = json.loads(x.userid)
        waitcrnlist.append(str(x.crn) + str(regd))

      returnstr += '\n'.join(waitcrnlist)
      await message.channel.send(str(returnstr).strip())

client.run(token)