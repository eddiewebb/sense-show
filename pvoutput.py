import os
import datetime
import requests
from dotenv import load_dotenv
import sense_energy
import json

def main():
	load_dotenv()
	#authenticate once
	if os.getenv("PVOUTPUT_KEY"):
		trend = SenseTrend()
		pv = PvOutput()
		pv.postLive(trend.consumption())
		pv.postLive(trend.generation())
	else:
		print("To send stats to pvoutput.org, add key and id as described in readme.")


class PvOutput():
	def __init__(self):		
		key = os.getenv("PVOUTPUT_KEY")
		site_id = os.getenv("PVOUTPUT_ID")	
		self.headers = {"X-Pvoutput-Apikey": key, "X-Pvoutput-SystemId": site_id}

	def postLive(self, payload):
		url = "https://pvoutput.org/service/r2/addstatus.jsp"
		print("sending payload as:")
		print(payload)
		r=requests.post(url=url,headers=self.headers,data=payload)
		print(r.text)


class SenseTrend():
	def __init__(self):
		self.start=datetime.datetime.now()
		user = os.getenv("SENSE_USER")
		passwd = os.getenv("SENSE_PASSWD")	
		self.sense = sense_energy.Senseable(api_timeout=10)
		self.sense.authenticate(user, passwd)


	def load_live_status(self):
		asString = self.start.strftime('%Y-%m-%dT%X')
		print("Date used with sense: " + asString)
		self.data=self.sense.api_call('app/history/trends?monitor_id=50403&scale=DAY&start=' + asString )
		self.sense.update_realtime()
		self.realtime = self.sense.get_realtime()

	def consumption(self):
		self.load_live_status()
		peak = self.get_peak_production()
		payload = {
			"d":self.get_date_as('%Y%m%d'),
			"t":self.get_date_as('%H:%M'),
			"v3":self.get_daily_consumption(),
			"v4":self.get_realtime_consumption()
		}
		return payload

	def generation(self):
		self.load_live_status()
		peak = self.get_peak_production()
		payload = {
			"d":self.get_date_as('%Y%m%d'),
			"t":self.get_date_as('%H:%M'),
			"v1":self.get_daily_production(),
			"v2":self.get_realtime_production(),
			"v6": sum(self.realtime['voltage'])
		}
		return payload

	def get_daily_production(self):
		return self.data['production']['total']*1000

	def get_realtime_production(self):
		return self.realtime['d_solar_w'] if self.realtime['d_solar_w']>=0 else 0

	def get_daily_consumption(self):
		return self.data['consumption']['total']*1000

	def get_realtime_consumption(self):
		return self.realtime['w']

	def get_daily_contribution(self):
		return self.data['to_grid']*1000

	def get_peak_production(self):
		high = 0
		hour = 0
		for step_index, value in enumerate(self.data['production']['totals']):
			if value > high:
				high = value
				hour = step_index
			
		return { "time": str(hour) + ':00', "value": high*1000 }

	def get_date_as(self, format):
		return self.start.strftime(format)


if __name__ == '__main__':
	print('Sense data export starting')
	main()
	