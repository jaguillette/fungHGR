import sys, json, requests
try:
	import sh
	shell=True
except:
	shell=False

try:
	HGR_ID = sys.argv[1]
except IndexError:
	HGR_ID = input("HGR ID: ")

try:
	LAT = float(sys.argv[2])
except IndexError:
	LAT = float(input("Latitude: "))

try:
	LNG = float(sys.argv[3])
except IndexError:
	LNG = float(input("Longitude: "))

dataset_file = "output/enhanced_dataset.json"
with open(dataset_file,'r',encoding='utf-8') as fp:
	dataset = json.load(fp)

dataset[HGR_ID]['geo'] = {}

url = "http://api.geonames.org/findNearbyPlaceName"
Q = {"lat":LAT,"lng":LNG,"username":"jaguillette","type":"json"}
R = requests.get(url,params=Q)
print(R.url)
geoinfo = R.json()

#No geonameId
dataset[HGR_ID]['geo']['pres_country'] = geoinfo['geonames'][0]['countryName']
dataset[HGR_ID]['geo']['x_coord'] = LAT #not from geonames
dataset[HGR_ID]['geo']['y_coord'] = LNG #not from geonames
dataset[HGR_ID]['geo']['coded'] = "manually"
dataset[HGR_ID]['geo']['country_code'] = geoinfo['geonames'][0]['countryCode']
dataset[HGR_ID]['geo']['pres_loc'] = geoinfo['geonames'][0]['adminName1']

with open(dataset_file,'w',encoding='utf-8') as fp:
	json.dump(dataset,fp,sort_keys=True,indent=2)

if shell:
	git = sh.git.bake(_cwd='/home/jeremy/Documents/pro/fung_library/gazetteer/fungHGR/')
	print(git.add(dataset_file))
	print(git.commit(m="Added {} to dataset with coordinates {}, {}".format(dataset[HGR_ID]['ru_old_orth'],LAT,LNG)))

#print("Georeferencing successfully added for {}.\nLocation currently corresponds to modern location {}, {}.".format(dataset[HGR_ID]['ru_old_orth'],dataset[HGR_ID]['geo']['pres_loc'],dataset[HGR_ID]['geo']['pres_country']))