import datetime
from string import Template

start = datetime.datetime.now().replace(hour=0,minute=0)

print(start)
s = Template('$hour:$minute,0,0,$total,$current')
while start.hour < 7:
	print(s.substitute(hour=start.hour,minute=start.minute,total=1000,current=200))
	start = start + datetime.timedelta(minutes=5)