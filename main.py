import requests
import time
import datetime

url = 'https://status.playstation.com/'

myURLs= ["https://status.playstation.com/",
         "https://slack-status.com/","https://health.aws.amazon.com/health/status",
         "https://status.cloud.microsoft/m365/referrer=serviceStatusRedirect"]


for i in myURLs:
    
    urlResponse = requests.get(url)
    print(urlResponse)

    #this block takes the raw time data in second and make it more readaable 
    currentTimestamp = time.time()

    #you have to create an object date time to convert to string for readability
    dt_object = datetime.datetime.fromtimestamp(currentTimestamp) 
    readable_time_string = dt_object.strftime("%Y-%m-%d %H:%M:%S") 
    
    if urlResponse.status_code == 200: # 200 mean OK
        print(i)
        print(readable_time_string)
        print('Your site is onliine!')
        print('')
    else:
        print(i)
        print('The site is down go touch grass')
        print('')
