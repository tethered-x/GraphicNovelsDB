import mysql.connector 
import sys
import json

host_name = input("Server hostname or IP: ")
port_num = input("Port number: ")
user_name = input("MySQL Username: ")
passwd = input("MySQL Password: ")

server_info = {
    "HOST": f"{host_name}",
    "USERNAME": f"{user_name}",
    "PASSWORD": f"{passwd}",
    "PORT": f"{port_num}"
}

try:
    mydb = mysql.connector.connect(
        host=f"{host_name}",
        user=f"{user_name}",
        password=f"{passwd}",
        port=f"{port_num}"
    )
    print("Successfully connected to MySQL.")
    server_json = json.dumps(server_info)
    # Saves Server Input into local json file
    file_path = 'server-info.json'
    with open(file_path, 'w') as file:
        json.dump(server_info, file, indent=4)
    print("Server info added to configuration.")

    mycursor = mydb.cursor()
except:
    print(f"Could not connect to MySQL on {host_name}. Verify that service is running, or double-check credentials.")

database_name = "mycomicsdb"

def create_new_db():
    create_db = f"CREATE DATABASE {database_name}"
    try:
        mycursor.execute(create_db)
        print(f"Database '{database_name}' successfully created.")
    except:
        print("Could not create new database.")

# List databases any verify that desired db doesn't already exist.
try:
    mycursor.execute("SHOW DATABASES")
except:
    print("Could not find existing databases.")
    sys.exit("Failed to connect. Please try again.")

doesDBExist = False
for x in mycursor:
    if database_name.lower() in x:
        doesDBExist = True
        print(f"DATABASE '{database_name}' ALREADY EXISTS. MOVING ON.")

if doesDBExist == False:
    create_new_db()

mydb = mysql.connector.connect(
        host=f"{host_name}",
        user=f"{user_name}",
        password=f"{passwd}",
        database=f"{database_name}",
        port=f"{port_num}"
    )

mycursor = mydb.cursor()
        
table_name = "graphicnovels"

mycursor.execute("SHOW TABLES")
doesTableExist = False
for x in mycursor:
    if table_name.lower() in x:
        doesTableExist = True
        print(f"TABLE '{table_name}' ALREADY EXISTS.")

if doesTableExist == False:
    try:
        create_table = f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), author VARCHAR(255), artist VARCHAR(255), company VARCHAR(255), covercost DECIMAL(5,2), resalevalue DECIMAL(5,2), series VARCHAR(255), sold BOOLEAN, listed BOOLEAN, link VARCHAR(255), upc_code VARCHAR(14))"
        mycursor.execute(create_table)
        print(f"Table '{table_name}' successfully created.")
    except:
        print("Could not create table.")

print("MySQL database installation completed.")