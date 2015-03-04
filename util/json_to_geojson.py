import json

with open("../output/enhanced_dataset.json","r",encoding='utf-8') as fp:
    db = json.load(fp)

geojson = {"features":[],"type":"FeatureCollection"}
for k,v in db.items():
    if 'geo' in v:
        feature = {"geometry":{'coordinates':[v['geo']['x_coord'],v['geo']['y_coord']],"type":"Point"},"type":"Feature"}
        feature['properties'] = v
        geojson['features'].append(feature)

with open("../output/enhanced_dataset.geojson","w",encoding='utf-8') as fp:
    json.dump(geojson,fp,sort_keys=True)