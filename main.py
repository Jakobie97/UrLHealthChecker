import requests, time, datetime, sqlite3, yaml, flask, json, traceback


# --- Configuration Reading -----------------------------------------------------------------------------------------
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
# --- End Configuration Reading -----------------------------------------------------------------------------------

# --- Database Setup ----------------------------------------------------------------------------------------------

connection = sqlite3.connect('./Database/MyUrlChecksDBStorage.db') #path to sql db file
cursor = connection.cursor() #helper that inserts the data

sqlInsertQuery = "INSERT INTO Url_Responses (url, status_code, timestamp) VALUES (?, ?, ?);"
sqlSelectQuery = "SELECT * FROM Url_Responses where status_code = 200;"

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Url_Responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        status_code INTEGER,
        timestamp TEXT
        )
    ''')
# --- Discord Notification Function ----------------------------------------------------------------------------- 
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

# --- URL Checking and Database Logging --------------------------------------------------------------------------------
#variables for counting up and downed urls------------------------------------------------------------------------------
myListofUrls = []
isUpCounter = 0
isDownCounter = 0

for i in myURLs:
    try:
        urlResponse = requests.get(i, timeout=REQUEST_TIMEOUT)
        current_status_code = urlResponse.status_code

        # Check if the site is UP (200-level status)
        if urlResponse.status_code == requests.codes.ok: # requests.codes.ok is 200
            isUpCounter += 1

            # Try to decode JSON (this might still fail even if status is 200)
            try:
                jsonResponse = urlResponse.json()
                print("Successfully parsed JSON response.")
                # print(jsonResponse) # Uncomment to see the actual JSON data
            except requests.exceptions.JSONDecodeError:
                print(f"Warning: {i} returned status 200, but content was not JSON.")
        
        else:
            # Handle non-200 OK statuses (e.g., 404, 500, etc.)
            print(f"{i} returned an error status code: {current_status_code} ({urlResponse.reason})")
            isDownCounter += 1

    except requests.exceptions.ConnectionError as e:
        # This catches "connection refused", DNS errors, etc.
        print(f"NETWORK ERROR accessing {i}: {e}")
        current_status_code = 'Connection Failed'
        isDownCounter += 1
        
    except requests.exceptions.Timeout as e:
        # Catches if the server takes too long to respond
        print(f"TIMEOUT ERROR accessing {i}: {e}")
        current_status_code = 'Timeout'
        isDownCounter += 1

    except requests.exceptions.RequestException as e:
        # Catches any other ambiguity from the requests library
        print(f"AN UNEXPECTED REQUEST ERROR occurred for {i}: {e}")
        current_status_code = 'Error'
        isDownCounter += 1
    #--------------------------------------------------------------------------------------------

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

        myListofUrls.append([i, urlResponse.status_code, readable_time_string])
        
    else:
        
        downedURL = i #sets variable for the downed url for notification purposes
        print(i)
        print(readable_time_string)
        print('The site is down. Go touch grass')


        print("#########################################")
        print(jsonResponse)  # Print the JSON response for debugging


        cursor.execute(sqlInsertQuery,(i,urlResponse.status_code,readable_time_string))
        print('')

connection.commit() #pushes to database

print("Your database has successfully logged theses entries! :)")
print("Total URLs Up: ", isUpCounter)
print("Total URLs Down: ", isDownCounter)




# --- Status Change Detection and Notification ---

previous_status = {}  # This stores {url: last_status_code}

for url in myURLs:
    # 1. Check current status
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        current = response.status_code
    except requests.exceptions.ConnectionError:
        current = 'DOWN'  # Or 0, or 'CONNECTION_ERROR'
    
    # 2. Get previous status for THIS URL
    previous = previous_status.get(url)  # Returns None if first time
    
    # 3. Compare and decide
    if previous is None:
        # First time seeing this URL - just store, no alert
        previous_status[url] = current
    
    elif current != previous:
    # STATUS CHANGED! Send ONE clear alert
        status_text = "UP" if current == 200 else "DOWN"
        previous_text = "UP" if previous == 200 else "DOWN"
    
        send_discord_notification(discord_webhook_url, f"🚨 {url} changed from {previous} to {current}")
    
    previous_status[url] = current  # Update stored status
    # Log to database as usual
    
    cursor.execute(sqlInsertQuery, (url, current, readable_time_string))


   
    


connection.close()

send_discord_notification(discord_webhook_url, f"The URL Health Check completed. Check the database for results 🧾✅")
send_discord_notification(discord_webhook_url, f"Total URLs Up: {isUpCounter} \nTotal URLs Down: {isDownCounter}")# --- End Status Change Detection and Notification ---
    
  
