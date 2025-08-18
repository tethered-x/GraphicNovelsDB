import mysql.connector ### For connecting to MySQL Database and do DB things
import os ### To clear screen
import bcrypt ### Encrypts password for secret menu
from tabulate import tabulate ### Formats lists to look nice
import csv ## To export list to csv files
from datetime import datetime ### To add timestamp to csv file
import random ### If UPC is blank

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

#### IMPORT SERVER INFO FROM server-info.json
import json
file_path = 'server-info.json'
with open(file_path, 'r') as file:
    data = json.load(file)

host_name = data["HOST"]
user_name = data["USERNAME"]
passwd = data["PASSWORD"]
port_num = data["PORT"]
database_name = "mycomicsdb"

clear_screen()

mydb = mysql.connector.connect(
    host=f"{host_name}",
    user=f"{user_name}",
    password=f"{passwd}",
    port=f"{port_num}",
    database=f"{database_name}"
)

mycursor = mydb.cursor()

# Used for the reset index count hidden option
hashed_secret_password = b'$2b$12$QbnFFZl2oJrXSfXzZcnM0uc.Dc0G8ovA1cml0O7tgnqpfjKZh.j1.'
### ADDS SOME COLORED TEXT
RED = "\033[91m"
RESET = "\033[0m"

### [TO-DO]: Remove this secret menu/secret password stuff.
### Encrypt Password for Secret Menu Options
# secret_password = "CHANGEME"
# salt = bcrypt.gensalt()
# hashed_password = bcrypt.hashpw(secret_password, salt)
# print(hashed_password)

clear_screen()

def format_page_header(title):
    pretty_title_decoration = ""
    pretty_title = ""
    for letter in title:
        pretty_title += letter
    for x in pretty_title:
        pretty_title_decoration = pretty_title_decoration + "="
    print(f"\n  {pretty_title_decoration}  ")
    print(f"| {pretty_title} |")
    print(f"  {pretty_title_decoration}  \n")
        

### LIST ALL GRAPHIC NOVELS
def gn_list_all():
    exportRunning = True
    while exportRunning:
        mycursor.execute("SELECT title, author, artist, company, listed, sold, link, upc_code FROM graphicnovels ORDER BY title")
        myresult = mycursor.fetchall()
        i = 0
        gn_list = []
        for x in myresult:
            i = i + 1
            gn_list.append(x)
        format_page_header(f"The Collection So Far: {i} Total")
        print("")
        print(tabulate(gn_list, headers=["TITLE", "WRITER", "ARTIST", "PUBLISHER", "LISTED", "SOLD", "LINK", "UPC CODE"]))
        print("")
    
        exportOption = input(f"{RED}Export list to CSV? (y/n): {RESET}").upper()
        clear_screen()
        if exportOption == 'Y':
            export_list_to_csv()
            exportRunning = False
        elif exportOption == 'N':
            exportRunning = False

def generate_upc_code():
    random_number = random.randint(10000000000, 99999999999)
    prefix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    random_prefix = random.randint(0,25)
    random_prefix = prefix[random_prefix]
    # maybe I can add something here that verifies random is not identical to another code
    upc_code = random_prefix + "-" + str(random_number)
    print(f"Barcode was blank. Assigned {upc_code} as UPC Code.")
    return upc_code

### ADD GRAPHIC NOVEL
def gn_add():
    format_page_header("The Last 5 Added")
    print("")
    mycursor.execute("SELECT title, author, artist, company, covercost, resalevalue, sold, listed, link FROM graphicnovels")
    myresult = mycursor.fetchall()
    gn_list = []
    for x in myresult:
        gn_list.append(x)
    print(tabulate(gn_list[-5:], headers=["TITLE", "WRITER", "ARTIST", "PUBLISHER", "COST", "RESALE", "SOLD", "LISTED", "LINK"]))
    format_page_header("Add New Graphic Novel")
    upc_code = input("SCAN BARCODE (hit enter if none): ")
    if upc_code == "":
        upc_code = generate_upc_code()
    title = input("TITLE: ")
    author = input("WRITER: ")
    artist = input("ARTIST: ")
    company = input("COMPANY: ")
    covercost = input("RETAIL COST: ")
    resalevalue = input("RESALE VALUE: ")
    series = input("SERIES: ")
    sold = input("Sold? (1 = True/0 = False): ")
    listed = input("Lised on eBay? (1 = True/0 = False): ")
    link = input("Paste eBay link (or leave blank if none): ")

    try:
        sql = "INSERT INTO graphicnovels (title, author, artist, company, covercost, resalevalue, series, sold, listed, link, upc_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (title, author, artist, company, covercost, resalevalue, series, int(sold), int(listed), link, upc_code)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
    except:
        print("Add failed. Try again.")

# List GNs for the Modify Menu Options
def list_for_mod(menu_choice):
    gn_list = []
    myresult = []
    isSold = False
    match menu_choice:
        case "DELETE":
            mycursor.execute("SELECT id, title, author, artist, company FROM graphicnovels")
        case "UPC":
            mycursor.execute('SELECT id, title, author, artist, company FROM graphicnovels WHERE upc_code IS NULL')
        case "EBAY":
            mycursor.execute('SELECT id, title, author, artist, company FROM graphicnovels WHERE link IS NULL') 
        case "SOLD":
            mycursor.execute('SELECT id, title, author, artist, company, link FROM graphicnovels WHERE listed = 1 AND link IS NOT NULL')
            isSold = True
    myresult = mycursor.fetchall()
    for x in myresult:
        gn_list.append(x)
    if isSold == True:
        print(tabulate(gn_list, headers=["ID", "TITLE", "WRITER", "ARTIST", "PUBLISHER", "LINK"]))
    else:
        print(tabulate(gn_list, headers=["ID", "TITLE", "WRITER", "ARTIST", "PUBLISHER"]))

### DELETE GRAPHIC NOVEL, ASKS FOR RECORD ID or BARCODE
def gn_delete():
    format_page_header("Delete a Graphic Novel")
    print("")
    upc_code = input("Scan Barcode (or hit enter if none): ")
    sql = ""
    val = ()
    if upc_code == "":
        list_for_mod("DELETE")
        print("")
        userChoice = input("ID of Graphic Novel to Delete: ")
        sql = "DELETE FROM graphicnovels WHERE id = %s"
        val = (userChoice,)
    elif upc_code != "":
        sql = "DELETE FROM graphicnovels WHERE upc_code = %s"
        val = (upc_code,)
    mycursor.execute(sql, val)
    mydb.commit()
    print("Record deleted.")

### SECRET ITEM OPTION, RESETS ID BACK TO 1
# ONLY WORKS IF ALL RECORDS DELETED
def reset_count():
    password = input("Enter Password: ")
    # Had to convert string into byte string to work with bcrypt
    password = password.encode(encoding="utf-8")
    if bcrypt.checkpw(password, hashed_secret_password):
        try:
            sql = "ALTER TABLE graphicnovels AUTO_INCREMENT = 1"
            mycursor.execute(sql)
            print("Count reset.")
        except:
            print("Count reset failed.")
    else:
        print("Incorrect password. Operation not permitted.")

# Mark if an item is sold. Look up by barcode only. 
# This might be a problem for books without barcodes. 
def gn_mark_sold():
    format_page_header("Mark Item Sold")
    print("")
    link = ""
    list = 0
    sold = 1
    code = input("Scan Barcode (or hit return if none): ")
    if code == "":
            print("")
            list_for_mod("SOLD")
            print("")
            code = input("Record ID: ")
            sql = "UPDATE graphicnovels SET link = %s, listed = %s, sold = %s WHERE id = %s"
    elif code != "":
        sql = "UPDATE graphicnovels SET link = %s, listed = %s, sold = %s WHERE upc_code = %s"
        val = (link, list, sold, code)
    val = (link, list, sold, code)
    if code != "":
        try:
            mycursor.execute(sql, val)
            print("Item marked as sold.")
        except:
            print("Could not update record. Please try again.")
    elif code == "":
        print("No code provided. Nothing to do.")
    
# Adds eBay Link, searches by UPC code or ID
def gn_add_link():
    format_page_header("Add eBay Link")
    print("")
    code = input("Scan Barcode (or hit return if none): ")
    if code == "":
        print("")
        list_for_mod("EBAY")
        print("")
        code = input("Record ID: ")
        sql = "UPDATE graphicnovels SET link = %s, listed = %s WHERE id = %s"
    elif code != "":
        sql = "UPDATE graphicnovels SET link = %s, listed = %s WHERE upc_code = %s"
    ebay_link = input("Paste eBay link: ")
    listed = 1
    val = (ebay_link, listed, code)
    if code != "":
        try:
            mycursor.execute(sql, val)
            mydb.commit()
            print(f"Record with code: {code} successfully updated.")
        except:
            print("Record update failed.")
    elif code == "":
        print("No code provided. Nothing to do.")

# Adds UPC code if one doesn't exist
def gn_add_upc_code():
    format_page_header("Add UPC Code")
    print("")
    list_for_mod("UPC")
    print("")
    comic_id = input("ID of graphic novel to update: ")
    if comic_id != "":
        upc_code = input("Scan Barcode: ")
        if upc_code == "":
            upc_code = generate_upc_code()
        sql = "UPDATE graphicnovels SET upc_code = %s WHERE id = %s"
        val = (upc_code, comic_id)
        try:
            mycursor.execute(sql, val)
            mydb.commit()
            print(f"Record #{comic_id} successfully updated.")
        except:
            print("Record update failed.")
    else:
        print("No ID provided. Nothing to do.")

# Exports Table to CSV
def export_list_to_csv():
    print("")
    timestamp = datetime.now()
    formatted_time = timestamp.strftime("%b-%d-%Y-%H%M%S")
    name_of_file = f"GraphicNovelList-{formatted_time}"
    print(f"{name_of_file}.csv")
    mycursor.execute("SELECT * FROM graphicnovels")
    myresult = mycursor.fetchall()
    csv_list = []
    for x in myresult:
        csv_list.append(x)
    #print(gn_list)
    csv_header_list = [('id', 'title', 'writer', 'artist', 'publisher', 'cover price', 'resale value', 'series', 'item sold', 'listed on ebay', 'ebay link', 'upc code')]
    csv_list = csv_header_list + csv_list
    try:
        with open(f'{name_of_file}.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(csv_list)
        print("CSV List Exported Successfully.")
    except:
        print("CSV Export Failed.")

# sub menu for modifying a record
def mod_gn_menu():
    menuRunning = True
    while menuRunning:
        format_page_header("Graphic Novel Modify Menu")
        print(f"{RED}Please select from the following options.{RESET}")
        print("1. Add eBay Link to a Record")
        print("2. Add UPC Code to a Record")
        print("3. List Item as Sold")
        print("Q. Return to Main Menu")
        print("")
        menuOptionChosen = input("Option: ").upper()
        clear_screen()
        match menuOptionChosen:
            case "1":
                gn_add_link()
            case "2":
                gn_add_upc_code()
            case "3":
                gn_mark_sold()
            case "Q":
                clear_screen()
                menuRunning = False
            case _:
                print("Option Not Found.")
        print("")
    
### MAIN PROGRAM
programRunning = True
while programRunning:
    format_page_header("Matt's Graphic Novel Collection")
    program_title = "Matt's Graphic Novels"
    os.system(f'title {program_title}')
    print("")
    print(f"{RED}Please select from the following options.{RESET}")
    print("1. Add a New Record")
    print("2. Delete a Record")
    print("3. List All Records")
    print("4. Modify a Record")
    print("5. CSV Quick Export")
    print("Q. Quit Program")
    print("")
    userChoice = input("Option: ").upper()
    clear_screen()
    match userChoice:
        case "1":
            gn_add()
        case "2":
            gn_delete()
        case "3":
            gn_list_all()
        case "4":
            mod_gn_menu()
        case "5":
            export_list_to_csv()
        case "Q":
            clear_screen()
            programRunning = False
        case "R":
            # SECRET MENU OPTION, PASSWORD PROTECTED
            reset_count()
        case _:
            print("Option Not Found.")
    print("")

### [TO-DO]:
# Code doesn't check against provided values to see if UPC matches something or ID matches something
# It will just say that the operation is completed but doesn't actually do anything. 