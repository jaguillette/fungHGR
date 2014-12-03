import sys, json, requests, time, sh, re
import pandas as pd
from lxml import html

#TRANSLITERATION FUNCTION
cyrillic_translit={u'\u0410': 'A', u'\u0430': 'a',u'\u0411': 'B', u'\u0431': 'b',u'\u0412': 'V', u'\u0432': 'v',u'\u0413': 'G', u'\u0433': 'g',u'\u0414': 'D', u'\u0434': 'd',u'\u0415': 'E', u'\u0435': 'e',u'\u0416': 'Zh', u'\u0436': 'zh',u'\u0417': 'Z', u'\u0437': 'z',u'\u0418': 'I', u'\u0438': 'i',u'\u0419': 'I', u'\u0439': 'i',u'\u041a': 'K', u'\u043a': 'k',u'\u041b': 'L', u'\u043b': 'l',u'\u041c': 'M', u'\u043c': 'm',u'\u041d': 'N', u'\u043d': 'n',u'\u041e': 'O', u'\u043e': 'o',u'\u041f': 'P', u'\u043f': 'p',u'\u0420': 'R', u'\u0440': 'r',u'\u0421': 'S', u'\u0441': 's',u'\u0422': 'T', u'\u0442': 't',u'\u0423': 'U', u'\u0443': 'u',u'\u0424': 'F', u'\u0444': 'f',u'\u0425': 'Kh', u'\u0445': 'kh',u'\u0426': 'Ts', u'\u0446': 'ts',u'\u0427': 'Ch', u'\u0447': 'ch',u'\u0428': 'Sh', u'\u0448': 'sh',u'\u0429': 'Shch', u'\u0449': 'shch',u'\u042a': '"', u'\u044a': '"',u'\u042b': 'Y', u'\u044b': 'y',u'\u042c': "'", u'\u044c': "'",u'\u042d': 'E', u'\u044d': 'e',u'\u042e': 'Iu', u'\u044e': 'iu',u'\u042f': 'Ia', u'\u044f': 'ia',u'\u0462': 'E', u'\u0463': 'e'}

def transliterate(word, translit_table):
	"""
	Transliterates 'word' based on the key/value pairs in 'translit_table'
	"""
	converted_word = ''
	try:
		for char in word:
			transchar = ''
			if char in translit_table:
				transchar = translit_table[char]
			else:
				transchar = char
			converted_word += transchar
	except TypeError:
		pass
	return converted_word

with open("resources/special_cases.json",'r',encoding='utf-8') as fp:
    lookup_dict = json.load(fp)

def ortho_rules(text,lookup_dict):
    """
    Takes a text string and a lookup dict as input
    Removes any lingering html tags
    Breaks the string down into component words with split
    Uses replacements to modernize orthography
    Returns re-assembled text with modern orthography
    """
    if type(text)==str:
        text = html.fromstring(text).text_content()
        textlist = text.split(' ')
        out_list = []
        for word in textlist:
            if word in [',','.',';',':']:
                out_list.append(word)
            word = word.strip(',.;:')
            if word in lookup_dict:
                word = lookup_dict[word]
                out_list.append(word)
            else:
                word = re.sub("[Ъъ]$",'',word)
                word = re.sub(r"^([че]{0,2}[ч]?[вбнр]?[веоаи])з([ПФКТШСЧпфктшсч])",r"\1с\2",word,re.IGNORECASE)
                word = re.sub("аго$","ого",word,re.IGNORECASE)
                word = re.sub("яго$","его",word,re.IGNORECASE)
                word = re.sub("ыя$","ые",word,re.IGNORECASE)
                word = re.sub("iя$","ие",word,re.IGNORECASE)
                word = word.replace('i','и') #english
                word = word.replace('I','И') #english
                word = word.replace('і','и') #cyrillic
                word = word.replace('І','И') #cyrillic
                word = word.replace('Ѣ','Е')
                word = word.replace('ѣ','е')
                word = word.replace('Ѳ','Ф')
                word = word.replace('ѳ','ф')
                out_list.append(word)
        out_str = ' '.join(out_list)
        return out_str
    else:
        return None

#REVERSE GEOCODING FUNCTION
def reverse_geocode(lng,lat):
	keepgoing = True
	while keepgoing == True:
		try:
			url = "https://maps.googleapis.com/maps/api/geocode/json"
			Q = {'latlng':"{},{}".format(lat,lng)}
			R = requests.get(url, params=Q)
			print(R.url)
			geo_response = R.json()
			locality = 'error'
			for component in geo_response['results'][0]['address_components']:
				if 'locality' in component['types']:
					locality = component['long_name']
				elif 'administrative_area_level_1' in component['types']:
					admin1 = component['long_name']
				elif 'country' in component['types']:
					country = component['long_name']
					countryCode = component['short_name']
			if locality == 'error':
				for component in geo_response['results'][0]['address_components']:
					if 'administrative_area_level_2' in component['types']:
						locality = component['long_name']
			print("\"{0}, {1}\",\"{2}\",\"{3}\"".format(locality,admin1,country,countryCode))
			time.sleep(1)
			keepgoing = False
		except IndexError:
			time.sleep(1)
			continue
		return "{}, {}".format(locality,admin1), country, countryCode

#ARGUMENTS FROM COMMAND LINE
try:
	geojson = sys.argv[1]
	geonameId = int(sys.argv[2])
except IndexError:
	print("This script takes two arguments, the name of a json file in geonames_jsons/geojson and an geonameId of a place found in that file.")
	sys.exit()

#FILE TO BE MODIFIED, CHANGE IF PRIMARY CSV CHANGES
file_to_append = "output/hgr_dataset.csv"

#DATA SETUP
dataset = pd.DataFrame.from_csv(file_to_append)
ind_to_add = max(dataset.index)+1

datum = {"ru_old_orth":{},"ru_new_orth":{},"lc_translit_old":{},"lc_translit_new":{},"alt_name_old_orth":{},"alt_name_new_orth":{},"alt_name_old_trans":{},"alt_name_new_trans":{},"beg_yr":{},"end_yr":{},"xy_type":{},"x_coord":{},"y_coord":{},"pres_loc":{},"pres_country":{},"country_code":{},"ru_old_featuretype":{},"ru_new_featuretype":{},"ru_translit_old_featuretype":{},"ru_translit_new_featuretype":{},"en_featuretype":{},"id_featuretype":{},"lc_featuretype":{},"admin_level":{},"SOURCE":{},"description":{},"geonameId":{},"partof_id":{},"txt_id":{}}

with open("geonames_jsons/geojson/{}".format(geojson), "r") as fp:
	geojson_dict = json.load(fp)

with open("resources/translate_types.json","r", encoding="utf-8") as fp:
	translate_types = json.load(fp)

#partof_prov_lookup_dict = dataset[dataset.partof_prov == dataset.index][['partof_prov_name']].to_dict()
#partof_uezd_lookup_dict = dataset[dataset.partof_uezd == dataset.index][['partof_uezd_name']].to_dict()

#GETTING DATA FROM GEOJSON DICT.
for v in geojson_dict['features']:
	if v['properties']['geonameId'] == geonameId:
		datum['ru_old_orth'][ind_to_add] = v['properties']['hgr_ru_old_orth']
		datum['ru_new_orth'][ind_to_add] = v['properties']['hgr_ru_new_orth']
		datum['lc_translit_old'][ind_to_add] = transliterate(v['properties']['hgr_ru_old_orth'],cyrillic_translit)
		datum['lc_translit_new'][ind_to_add] = transliterate(v['properties']['hgr_ru_new_orth'],cyrillic_translit)
		datum['alt_name_old_orth'][ind_to_add] = v['properties']['hgr_alt_name_old_orth']
		datum['alt_name_new_orth'][ind_to_add] = ortho_rules(v['properties']['hgr_alt_name_old_orth'],lookup_dict)
		datum['alt_name_old_trans'][ind_to_add] = transliterate(v['properties']['hgr_alt_name_old_orth'],cyrillic_translit)
		datum['alt_name_new_trans'][ind_to_add] = transliterate(datum['alt_name_new_orth'][ind_to_add],cyrillic_translit)
		datum['beg_yr'][ind_to_add] = ""
		datum['end_yr'][ind_to_add] = ""
		datum['xy_type'][ind_to_add] = "POINT"
		datum['x_coord'][ind_to_add] = v['geometry']['coordinates'][0]
		datum['y_coord'][ind_to_add] = v['geometry']['coordinates'][1]
		datum['partof_id'][ind_to_add] = v['properties']['hgr_partof_id']
		datum['ru_old_featuretype'][ind_to_add] = v['properties']['hgr_ru_old_featuretype']
		datum['ru_new_featuretype'][ind_to_add] = ortho_rules(v['properties']['hgr_ru_old_featuretype'],lookup_dict)
		datum['ru_translit_old_featuretype'][ind_to_add] = transliterate(datum['ru_old_featuretype'][ind_to_add],cyrillic_translit)
		datum['ru_translit_new_featuretype'][ind_to_add] = transliterate(datum['ru_new_featuretype'][ind_to_add],cyrillic_translit)
		datum['en_featuretype'][ind_to_add] = translate_types[datum['ru_new_featuretype'][ind_to_add]]
		datum['id_featuretype'][ind_to_add] = ""
		datum['lc_featuretype'][ind_to_add] = ""
		datum['admin_level'][ind_to_add] = "locality"
		datum['SOURCE'][ind_to_add] = v['properties']['hgr_SOURCE']
		datum['description'][ind_to_add] = v['properties']['hgr_description']
		datum['geonameId'][ind_to_add] = "http://geonames.org/{}".format(v['properties']['geonameId'])
		datum['partof_id'][ind_to_add] = v['properties']['hgr_partof_id']
		datum['txt_id'][ind_to_add] = v['properties']['hgr_txt_id']
		found = True

if found != True:
	print("ID was not found in the specified file. Please make sure that the ID {} is present in the file {}".format(geonameId,geojson))
	sys.exit()

#REVERSE GEOCODING FOR PRESENT LOCATION FROM GOOGLE
datum['pres_loc'][ind_to_add], datum['pres_country'][ind_to_add], datum['country_code'][ind_to_add] = reverse_geocode(datum['x_coord'][ind_to_add],datum['y_coord'][ind_to_add])

#SETTING UP DATAFRAME FOR EXPORT. APPEND DATA, ORDER COLUMNS, AND NAME INDEX.
dataset = dataset.append(pd.DataFrame(datum))
dataset = dataset[["ru_old_orth","ru_new_orth","lc_translit_old","lc_translit_new","alt_name_old_orth","alt_name_new_orth","alt_name_old_trans","alt_name_new_trans","beg_yr","end_yr","xy_type","x_coord","y_coord","pres_loc","pres_country","country_code","ru_old_featuretype","ru_new_featuretype","ru_translit_old_featuretype","ru_translit_new_featuretype","en_featuretype","id_featuretype","lc_featuretype","admin_level","SOURCE","description","geonameId","partof_id","hgr_id","txt_id"]]
dataset.index.name = 'uniq_id'

dataset.to_csv(file_to_append,encoding='utf=8')

git = sh.git.bake(_cwd='/home/jeremy/Documents/pro/fung_library/gazetteer/fungHGR/')
print(git.add(file_to_append))
print(git.commit(m="Added {} to dataset after confirming it corresponds to GeoNames ID {}".format(datum['lc_translit_new'][ind_to_add],geonameId)))