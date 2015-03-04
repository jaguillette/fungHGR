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
	GEO_ID = int(sys.argv[2])
except IndexError:
	GEO_ID = int(input("Geonames ID: "))

dataset_file = "output/enhanced_dataset.json"
with open(dataset_file,'r',encoding='utf-8') as fp:
	dataset = json.load(fp)

dataset[HGR_ID]['geo'] = {}

R = requests.get("http://api.geonames.org/getJSON?geonameId={}&username=jaguillette".format(GEO_ID))
geoinfo = R.json()

dataset[HGR_ID]['geo']['geonameId'] = "http://www.geonames.org/{}".format(GEO_ID)
dataset[HGR_ID]['geo']['pres_country'] = geoinfo['countryName']
dataset[HGR_ID]['geo']['x_coord'] = geoinfo['lng']
dataset[HGR_ID]['geo']['y_coord'] = geoinfo['lat']
dataset[HGR_ID]['geo']['coded'] = "manually"
dataset[HGR_ID]['geo']['country_code'] = geoinfo['countryCode']
dataset[HGR_ID]['geo']['pres_loc'] = "{}, {}".format(geoinfo['name'],geoinfo['adminName1'])

with open(dataset_file,'w',encoding='utf-8') as fp:
	json.dump(dataset,fp,sort_keys=True,indent=2)

if shell:
	git = sh.git.bake(_cwd='/home/jeremy/Documents/pro/fung_library/gazetteer/fungHGR/')
	print(git.add(dataset_file))
	print(git.commit(m="Added {} to dataset after confirming it corresponds to GeoNames ID {}".format(dataset[HGR_ID]['name_old_orth'],GEO_ID)))

#print("Georeferencing successfully added for {}.\nLocation currently corresponds to modern location {}, {}.".format(dataset[HGR_ID]['ru_old_orth'],dataset[HGR_ID]['geo']['pres_loc'],dataset[HGR_ID]['geo']['pres_country']))