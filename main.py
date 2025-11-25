import requests

url = 'https://status.playstation.com/'

response = requests.get(url)

if response.status_code == 200:
    print('')
    print('The Play Station Network is onliine!')
else:
    print('')
    print('The site is down go touch grass')

print('')
print(response)