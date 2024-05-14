import requests
headers = {
'Content-Type': 'application/json',
'Authorization': 'Bearer vgEADQAAAA9iY2dkdi5sb3Jpb3QuaW-ve6WTseo19HasKoGVQJS1',
}
data = '{ "cmd": "tx", "EUI": "5C7C5824000054B9", "port": 69, "confirmed": true, "data": "Tumbledown", "appid": "BE01000D" }'
response = requests.post('https://us1.loriot.io/1/rest', headers=headers, data=data)