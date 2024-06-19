import requests
import datetime
import smtplib
import time
import os

MY_LAT = os.environ.get('MY_LAT')
MY_LONG = os.environ.get('MY_LONG')

MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get('MY_PASSWORD')

response = requests.get(url="http://api.open-notify.org/iss-now.json")
response.raise_for_status()
data = response.json()

iss_latitude = float(data["iss_position"]["latitude"])
iss_longitude = float(data["iss_position"]["longitude"])

parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}

response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
data = response.json()
sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

time_now = datetime.datetime.now()
hour = time_now.hour

while True:
    time.sleep(60)
    if hour > sunset or hour < sunrise:
        if -5 < iss_latitude - MY_LAT < 5 and -5 < iss_longitude - MY_LONG < 5:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(password=MY_PASSWORD, user=MY_EMAIL)
                connection.sendmail(from_addr=MY_EMAIL,
                                    to_addrs=os.environ.get('TO_ADDRESS'),
                                    msg="Subject:ISS is overhead\n\nGo look for iss in the sky")
