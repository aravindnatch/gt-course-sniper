import requests
import concurrent
from concurrent.futures import ThreadPoolExecutor
import time
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import peewee
import json
from dhooks import Webhook
import subprocess
from twilio.rest import Client

# https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term=202308&courseReferenceNumber=84588

load_dotenv()
term = os.getenv('term')
betahook = os.getenv("beta_webhook")
publichook = os.getenv("public_webhook")

db = peewee.SqliteDatabase('../db/main.sqlite', pragmas={'journal_mode': 'wal', 'synchronous': 'full'})
class Classes(peewee.Model):
  crn=peewee.CharField(unique=True)
  status=peewee.CharField()
  userid=peewee.CharField()
  name=peewee.CharField()
  class Meta:
    database=db
    db_table='Classes'

base_url = 'https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo'
threads = 30

def heartbeat():
	try:
		data = {
			"content" : 'Last Beta Heartbeat: ' + time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))
		}
		requests.patch(betahook, json=data)
	except Exception as e:
		print(str(e))

def log(text):
  print(text)
  file1 = open("betalog.txt", "a")
  file1.write(text)
  file1.close()

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
}

def getCRN(crn):
  req = requests.get(f"{base_url}?term={term}&courseReferenceNumber={crn}", headers=headers, timeout=2)
  return req

heartbeat()

while True:
  try:
    startTime = time.time()
    with ThreadPoolExecutor(max_workers=threads) as executor:
      crns = Classes.select()
      future_to_url = []
      mapping = {}
      for x in crns:
        future = executor.submit(getCRN, x.crn)
        mapping[future] = x
        future_to_url.append(future)
        
      for future in concurrent.futures.as_completed(future_to_url):
        try:
          x = mapping[future]
          crn_id = x.crn
          req = future.result()

          if req.status_code == 200:
            soup = BeautifulSoup(req.text, 'html.parser')
            capacity = int(soup.find('span', string="Enrollment Maximum:").find_next('span').text.strip())
            actual = int(soup.find('span', string="Enrollment Actual:").find_next('span').text.strip())
            remaining = int(soup.find('span', string="Enrollment Seats Available:").find_next('span').text.strip())
            waitlistremaining = int(soup.find('span', string="Waitlist Actual:").find_next('span').text.strip())
            status = x.status
            if (status == "closed") and (remaining > 0) and (waitlistremaining == 0):
              status = "open"
              row=Classes.get(Classes.crn==x.crn)
              row.status = status
              row.save()
            elif (status == "open") and ((remaining == 0) or (waitlistremaining > 0)):
              status = "closed"
              row=Classes.get(Classes.crn==x.crn)
              row.status = status
              row.save()

            sendtext = ""
            courseTitle = x.name
            if status != x.status:
              sendtext+="UPDATE: " + status.upper() + "\n\n"
              sendtext+= courseTitle + "\n"
              sendtext+= "Capacity: " + str(capacity) + "\n"
              sendtext+= "Actual: " + str(actual) + "\n"
              sendtext+= "Remaining: " + str(remaining) + "\n"

              userids = json.loads(x.userid)
              userlist = ''
              for x in userids:
                userlist+=f'<@{x}> '
              userlist = userlist.strip()
              hook = Webhook(publichook)
              hook.send(userlist + "\n" + sendtext)

              # if status.lower() == "open":
              #   if "" in userids:
              #     # Your Twilio account SID and Auth Token
              #     try:
              #       ACCOUNT_SID = ''
              #       AUTH_TOKEN = ''

              #       # Initialize the Twilio client
              #       client = Client(ACCOUNT_SID, AUTH_TOKEN)

              #       # Make a phone call
              #       call = client.calls.create(
              #         to="",  # The phone number you want to call
              #         from_="+18557693898", # Your Twilio number
              #         url="http://demo.twilio.com/docs/voice.xml"  # A URL with TwiML instructions for the call
              #       )
              #     except Exception as e:
              #       log(str(e) + "\n")
                  # subprocess.Popen(["python3", "/home/aravindnatch/server/coursesniper/snipers/aravind/main.py", crn_id])

            print(courseTitle)
          else:
            log(f'status code ({time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))}): {str(req.status_code)}\n')
            time.sleep(1)
        except Exception as e:
          heartbeat()
          knownErrors = ['ConnectionError', 'ReadTimeout', 'ConnectTimeout']
          time.sleep(1)

          if type(e). __name__ not in knownErrors:
            log(f'error ({time.strftime("%m/%d/%Y %I:%M:%S %p", time.gmtime(time.time() - 18000))}): {str(e)}\n')
            log(f"Exception name: {type(e). __name__}\n")
            
          break
      endTime = time.time()
      print(f"\033[92m{str(endTime-startTime)} seconds, {len(crns)} crns\033[0m")
  except Exception as e:
    log(str(e) + "\n")

  print("--------")
