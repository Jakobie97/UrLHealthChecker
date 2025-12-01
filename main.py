import requests, time, datetime, sqlite3, yaml


# --- Configuration Reading ---
try:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("Error: config.yaml file not found.")
    exit()

# Assign the values from the config file to variables
myURLs = config['urls_to_monitor']
REQUEST_TIMEOUT = config['settings']['request_timeout_seconds']
CHECK_FREQUENCY = config['settings']['check_frequency_minutes']
# --- End Configuration Reading ---

connection = sqlite3.connect('./Database/MyUrlChecksDBStorage.db') #path to sql db file
cursor = connection.cursor() #helper that inserts the data

sqlInsertQuery = "INSERT INTO Url_Responses (url, status_code, timestamp) VALUES (?, ?, ?);"

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Url_Responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        status_code INTEGER,
        timestamp TEXT
        )
    ''')
  

#myURLs= ["https://status.playstation.com/",
#        "https://slack-status.com/","https://health.aws.amazon.com/health/status",
#        "https://status.cloud.microsoft/m365/referrer=serviceStatusRedirect"]


for i in myURLs:
    
    urlResponse = requests.get(i, timeout=REQUEST_TIMEOUT)
    

    #this block takes the raw time data in second and make it more readaable 
    currentTimestamp = time.time()

    #you have to create an object date time to convert to string for readability
    dt_object = datetime.datetime.fromtimestamp(currentTimestamp) 
    readable_time_string = dt_object.strftime("%Y-%m-%d %H:%M:%S") 
    
    if urlResponse.status_code == 200: # 200 mean OK
        
        print(i)
        print(readable_time_string)
        print('Your site is online!')

        cursor.execute(sqlInsertQuery,(i,urlResponse.status_code,readable_time_string)) 
        print('')
        
    else:

        print(i)
        print(readable_time_string)
        print('The site is down. Go touch grass')

        cursor.execute(sqlInsertQuery,(i,urlResponse.status_code,readable_time_string))
        print('')

connection.commit() #pushes to database

print("Your database has successfully logged theses entries! :)")
print(f"Next check in {CHECK_FREQUENCY} minutes.")
connection.close()
    
  
