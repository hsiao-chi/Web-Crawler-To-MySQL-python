import re
import requests as que
import time
import json
import MySQLdb
import urllib
import gzip
#------dataBase connect-------------
db = MySQLdb.connect(host="localhost", 
					user="userName", 
					passwd="passwd", 
					db="databaseName",
					use_unicode=True,
					charset="utf8")
cursor = db.cursor()

#-------------------------------------
def getGas_Price():
	url = "http://new.cpc.com.tw/Home/"
	url1 = "http://www.fpcc.com.tw/tc/affiliate.php"
	pat = "<dd>(\w+)&nbsp;&nbsp;<strong>(\d+\.\d+)</strong>"
	pat1 = "\$(\d+\.\d+)"
	data = que.get(url).text
	data1 = que.get(url1).text
	find = re.findall( pat, data, re.UNICODE )
	find1 = re.findall(pat1,data1 )
	str = [u'中油',u'台塑']
#	for i in range(len(find)):
#		if i != 3 and i != 5:
#			name, price = find[i]
#			print price.encode('big5')
	cursor.execute("""INSERT INTO  gas_price(company,p92,p95,p98,pdiesel) VALUES(%s,%s,%s,%s,%s)""",
					(str[0],find[0][1],find[1][1],find[2][1],find[4][1]))
#	for i in range(len(find1)):
#		if i<4:
#			price = find1[i]
#			print price.encode('big5')
	cursor.execute("""INSERT INTO  gas_price(company,p92,p95,p98,pdiesel) VALUES(%s,%s,%s,%s,%s)""",
					(str[1],find1[0],find1[1],find1[2],find1[3]))
	
#-------------------------------------------------------	
def park_NTP():
	r = que.get('http://data.ntpc.gov.tw/od/data/api/E09B35A5-A738-48CC-B0F5-570B67AD9C78?$format=json')
	doc = json.loads(r.text)
	i = 0
	while i<len(doc):
		str = "%s, %d"%(doc[i]['ID'],int(doc[i]['AVAILABLECAR']))
#		print str
		cursor.execute("""INSERT INTO newtaipei_park_d (ID_1,avail) VALUES(%s,%s)""",(doc[i]['ID'],doc[i]['AVAILABLECAR']))
		i+=1;
#	db.commit()
	
#------------------------------------------------------------

def park_TP():
	url = "http://data.taipei/tcmsv/allavailable"
	urllib.urlretrieve(url,"parkTP.gz")
	f = gzip.open('parkTP.gz','r')
	j = f.read()
	f.close()
	jdata = j.decode('big5').encode('utf-8')
	data = json.loads(jdata)

	for row in data['data']['park']:
		id = row['id']
		avail = row['availablecar']
		str = "%s, %d"%(id,int(avail))
		cursor.execute("""INSERT INTO taipei_park_d (ID_1,avail) VALUES(%s,%s)""",(id,avail))
		#print str

#----main--------------------------------------------------	
t=0
while True:
	if(t == 480):
		t=0
		getGas_Price()
	park_NTP()
	park_TP()
	db.commit()
	t+=1
	time.sleep(180)

db.close()		
