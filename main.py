import requests

url = 'https://status.playstation.com/'

myURLs= ["https://status.playstation.com/",
         "https://slack-status.com/","https://health.aws.amazon.com/health/status",
         "https://status.cloud.microsoft/m365/referrer=serviceStatusRedirect"]


for i in myURLs:
    urlResponse = requests.get(url)
    print(urlResponse)
    if urlResponse.status_code == 200:

        print(i)
        print('Your site is onliine!')
        print('')
    else:
        print(i)
        print('The site is down go touch grass')
        print('')
