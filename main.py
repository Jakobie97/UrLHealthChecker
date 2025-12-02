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
  
def send_discord_notification(webhook_url, message):
    data = {
        "content": message
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Notification sent to Discord successfully.")
        else:
            print(f"Failed to send notification to Discord. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending notification to Discord: {e}")

discord_webhook_url = config['discord_webhook']['url']

for i in myURLs:
    try:
        urlResponse = requests.get(i, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        print(f"Error accessing {i}: {e}")
        urlResponse = type('obj', (object,), {'status_code' : 'N/A'})()  # Create a dummy object with status_code 'N/A'

    #this block takes the raw time data in second and make it more readaable 
    currentTimestamp = time.time()

    #you have to create an object date time to convert to string for readability
    dt_object = datetime.datetime.fromtimestamp(currentTimestamp) 
    readable_time_string = dt_object.strftime("%Y-%m-%d %H:%M:%S") 

    myListofUrls = []
    
    if urlResponse.status_code == 200: # 200 mean OK
        
        print(i)
        print(readable_time_string)
        print('Your site is online!')

        myListofUrls.append(i)

        cursor.execute(sqlInsertQuery,(i,urlResponse.status_code,readable_time_string)) 
        print('')
        
    else:
        downedURL = i #sets variable for the downed url for notification purposes
        print(i)
        print(readable_time_string)
        print('The site is down. Go touch grass')

        cursor.execute(sqlInsertQuery,(i,urlResponse.status_code,readable_time_string))
        print('')

connection.commit() #pushes to database

print("Your database has successfully logged theses entries! :)")


send_discord_notification(discord_webhook_url, f"The URL Health Check completed. Check the database for results 🧾✅")

for i in myURLs:
    try:
        urlResponse = requests.get(i, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        urlResponse = type('obj', (object,), {'status_code' : 'N/A'})()  # Create a dummy object with status_code 'N/A'

    if urlResponse.status_code != 200:
        downedURL = i
        send_discord_notification(discord_webhook_url, f"The url: {downedURL} appears to be down! ❌🚨")
    else:
        send_discord_notification(discord_webhook_url, f"The url: {i} appears to be up! ✅")
        continue


connection.close()
    
  
