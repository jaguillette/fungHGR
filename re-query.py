import requests, sys, json, urllib

try:
	import sh
	shell=True
except:
	shell=False

try:
	ID = sys.argv[1]
except IndexError:
	ID = input("Text ID: ")

URL = input("New query URL: ")

parsed_url = urllib.parse.urlparse(URL)
print(parsed_url.query)
url_params = urllib.parse.parse_qs(parsed_url.query,keep_blank_values=True)
print(url_params)
outfile_name = "geonames_jsons/{}_{}_f{}.geojson".format(ID,url_params['name'][0],url_params['fuzzy'][0])

R = requests.get(URL)
data = R.json()

geojson = geojson = {"features":[],"type":"FeatureCollection"}
for p in data['geonames']:
	feature = {"geometry":{'coordinates':[float(p['lng']),float(p['lat'])],"type":"Point"},"type":"Feature"}
	feature['properties'] = p
	geojson['features'].append(feature)

with open(outfile_name,'w',encoding='utf-8') as fp:
	json.dump(geojson,fp)

if shell:
	git = sh.git.bake(_cwd='/home/jeremy/Documents/pro/fung_library/gazetteer/fungHGR/')
	print(git.add(outfile_name))
	print(git.commit(m="Added new query in geojson for {}, ID {}.".format(url_params['name'][0],ID)))