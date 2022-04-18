import json

url = 'https://identitysso-cert.betfair.com/api/certlogin'
headers = {
    'X-Application': 'IJE2hh59JFLsqo1Z',
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}
data = {'name': 'marcosp199610', 'password': 'Mmm.415263'}
import requests

s = requests.Session()
s.cert = ('./certs/client-2048.crt', './certs/client-2048.pem')
r = s.post(url=url, data=data, headers=headers)
r