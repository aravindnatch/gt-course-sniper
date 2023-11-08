#######################
# USE BETA.PY INSTEAD #
#######################


# import requests
# from bs4 import BeautifulSoup
# import time
# import peewee
# import random
# from dhooks import Webhook
# from discord_webhook import DiscordWebhook
# import json
# from dotenv import load_dotenv
# import os

# load_dotenv()
# term = os.getenv('term')
# mainhook = os.getenv("main_webhook")

# db = peewee.SqliteDatabase('../db/main.sqlite', pragmas={'journal_mode': 'wal', 'synchronous': 'full'})
# class Classes(peewee.Model):
#    crn=peewee.CharField(unique=True)
#    status=peewee.CharField()
#    userid=peewee.CharField()
#    class Meta:
#       database=db
#       db_table='Classes'

# headers = {
# 	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
# }

# def heartbeat():
# 	try:
# 		data = {
# 			"content" : 'Last Main Heartbeat: ' + time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))
# 		}
# 		requests.patch(mainhook, json=data)
# 	except Exception as e:
# 		print(str(e))

# heartbeat()

# while True:
# 	try:
# 		crns = Classes.select()
# 		for x in crns:
# 			req = requests.get(f"https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in={term}&crn_in={x.crn}", headers=headers, timeout=10)
# 			if req.status_code == 200:
# 				rows = []
# 				soup = BeautifulSoup(req.text, 'html.parser')
# 				data = soup.findAll('table',{'class':'datadisplaytable'})[1]

# 				for row in data.findAll('td',{'class':'dddefault'}):
# 					rows.append(row)
				
# 				remaining = int(rows[2].text)
# 				status = x.status
# 				if (status == "closed") and (remaining > 0):
# 					status = "open"
# 					row=Classes.get(Classes.crn==x.crn)
# 					row.status = status
# 					row.save()
# 				elif (status == "open") and (remaining == 0):
# 					status = "closed"
# 					row=Classes.get(Classes.crn==x.crn)
# 					row.status = status
# 					row.save()

# 				sendtext = ""
# 				courseTitle = soup.findAll('th')[0].text
# 				if status != x.status:
# 					sendtext+="UPDATE: " + status.upper() + "\n\n"
# 					sendtext+= courseTitle + "\n"
# 					sendtext+= "Capacity: " + rows[0].text + "\n"
# 					sendtext+= "Actual: " + rows[1].text + "\n"
# 					sendtext+= "Remaining: " + rows[2].text + "\n"

# 					userids = json.loads(x.userid)
# 					userlist = ''
# 					for x in userids:
# 						userlist+=f'<@{x}> '
# 					userlist = userlist.strip()
# 					hook = Webhook('https://discord.com/api/webhooks/1008554616989949972/jFgLgi4nfvqva-9OUkpwMtzrq7ho6BOxDc4mw23IEYgFE0FlM6V1Ljrxjy2c1-ipoGOl')
# 					hook.send(userlist + "\n" + sendtext)
# 			else:
# 				print("won")
# 			# time.sleep(0.2)
# 			print(courseTitle)
# 	except Exception as e:
# 		heartbeat()
# 		knownErrors = ['ConnectionError', 'ReadTimeout', 'ConnectTimeout']
# 		time.sleep(10)

# 		if type(e). __name__ not in knownErrors:
# 			hook = Webhook('https://discord.com/api/webhooks/791107612706865163/CIbSgse6hFrMpmO3RbVvkWWD3lYjfelx4oX9kxzd16uWcHXKtgsARR_2jYvfTtre_J2r')
# 			hook.send(str(e)[0:1000])
# 			hook.send('sending type name')
# 			hook.send(type(e).__name__)
# 			time.sleep(10)

# 	print("-------")
