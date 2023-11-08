import requests
from bs4 import BeautifulSoup
import time
import peewee
import random
from dhooks import Webhook
from discord_webhook import DiscordWebhook
import json
import subprocess
from dotenv import load_dotenv
import os

load_dotenv()
term = os.getenv('term')
waithook = os.getenv("waitlist_webhook")

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

base_url = 'https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo'

try:
	data = {
			"content" : 'Last Waitlist Heartbeat: ' + time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))
	}
	requests.patch(waithook, json=data)
except Exception as e:
	print(str(e))

while True:
	try:
		crns = WaitlistClasses.select()
		for x in crns:
			req = requests.get(f"{base_url}?term={term}&courseReferenceNumber={x.crn}", headers=headers, timeout=10)
			if req.status_code == 200:
				soup = BeautifulSoup(req.text, 'html.parser')
				capacity = int(soup.find('span', string="Waitlist Capacity:").find_next('span').text.strip())
				actual = int(soup.find('span', string="Waitlist Actual:").find_next('span').text.strip())
				remaining = int(soup.find('span', string="Waitlist Seats Available:").find_next('span').text.strip())
				status = x.status
				if (status == "closed") and (remaining > 0):
					status = "open"
					row=WaitlistClasses.get(WaitlistClasses.crn==x.crn)
					row.status = status
					row.save()
				elif (status == "open") and (remaining == 0):
					status = "closed"
					row=WaitlistClasses.get(WaitlistClasses.crn==x.crn)
					row.status = status
					row.save()

				sendtext = ""
				courseTitle = x.name
				if status != x.status:
					sendtext+="WAITLIST UPDATE: " + status.upper() + "\n\n"
					sendtext+= courseTitle + "\n"
					sendtext+= "Course Capacity: " + str(capacity) + "\n"
					sendtext+= "Waitlist Actual: " + str(actual) + "\n"
					sendtext+= "Waitlist Remaining: " + str(remaining) + "\n"

					# if x.crn in ["84584"] and status == "open":
					# 	subprocess.Popen(["python3","arasnipe.py","84584"])

					userids = json.loads(x.userid)
					userlist = ''
					for x in userids:
						userlist+=f'<@{x}> '
					userlist = userlist.strip()
					hook = Webhook('https://discord.com/api/webhooks/1008554616989949972/jFgLgi4nfvqva-9OUkpwMtzrq7ho6BOxDc4mw23IEYgFE0FlM6V1Ljrxjy2c1-ipoGOl')
					hook.send(userlist + "\n" + sendtext)
			else:
				# hook = Webhook('https://discord.com/api/webhooks/874362578401361960/TRxJM6FsYn57RDyjqcn7uG2KNj3YyywLrFBT_Px7oxFw7Yn10QxDjqmnwh3LoO3BkSZc')
				# hook.send("<@398935841444986880> request failed with code: " + str(req.status_code))
				print("won")
			# time.sleep(0.2)
			print(courseTitle)
	except Exception as e:
		if type(e). __name__ == 'ConnectionError':
			print("connection error to oscar")
			try:
				data = {
						"content" : 'Last Waitlist Heartbeat: ' + time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))
				}
				requests.patch(waithook, json = data)
			except Exception as e:
				print(str(e))
			time.sleep(60)	
		elif type(e). __name__ == 'ReadTimeout':
			print("read timeout to oscar")
			try:
				data = {
						"content" : 'Last Waitlist Heartbeat: ' + time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))
				}
				requests.patch(waithook, json = data)
			except Exception as e:
				print(str(e))
			time.sleep(60)
		elif type(e). __name__ == 'ConnectTimeout':
			try:
				data = {
						"content" : 'Last Waitlist Heartbeat: ' + time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))
				}
				requests.patch(waithook, json = data)
			except Exception as e:
				print(str(e))
			time.sleep(60)
		else:
			hook = Webhook('https://discord.com/api/webhooks/791107612706865163/CIbSgse6hFrMpmO3RbVvkWWD3lYjfelx4oX9kxzd16uWcHXKtgsARR_2jYvfTtre_J2r')
			# hook.send("<@398935841444986880> something went wrong")
			hook.send(str(e)[0:1000])
			hook.send('sending type name')
			hook.send(type(e).__name__)
			time.sleep(60)

	print("-------")
