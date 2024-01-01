import urllib.request
import os
from database import SimpleSQLiteDB
import argparse
from rfc import * # type: ignore
from hashlib import sha256

def init():
    homedir = os.path.expanduser("~")
    os.mkdir(homedir + "/.rfc-finder", 0o755)
    os.mkdir(homedir + "/.rfc-finder/rfc", 0o755)

    db = SimpleSQLiteDB()
    db.create_tables()

    rfc_url = "https://www.ietf.org/download/rfc-index.txt"
    data = urllib.request.urlopen(rfc_url).read()
    hash = sha256(data).hexdigest()
    parse_rfc_webpage(data.decode(), "0001", db)

    db.insert_config_value("hash", hash) #hash value to check if updating is needed

def print_db_results(RFCs, error_message):
    if RFCs is None:
        print(error_message)
        exit()

    for rfc in RFCs:
        print("RFC number: " + str(rfc[0]))
        print("title: " + rfc[1])


def find_by_title(title):
    db = SimpleSQLiteDB()
    RFCs = db.search_by_title(title)
    print_db_results(RFCs, "No RFC's found with that title")
    
def find_by_author(author):
    db = SimpleSQLiteDB()
    RFCs = db.search_by_author(author)
    print_db_results(RFCs, "No RFC's found with that author!")

def update():
    rfc_url = "https://www.ietf.org/download/rfc-index.txt"
    data = urllib.request.urlopen(rfc_url).read()

    db = SimpleSQLiteDB()
    cur_hash = db.get_config_value("hash")
    assert cur_hash is not None

    new_hash = sha256(data).hexdigest()

    if cur_hash == new_hash: #Update is not needed
        print("RFC database already up to date!")
    else: #update database
        latest_rfc_number = str(db.get_latest_RFC_number())
        parse_rfc_webpage(data.decode(), latest_rfc_number, db)
        db.insert_config_value("hash", new_hash)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to get information of RFC's from the commandline")

    parser.add_argument("-a", "--author", type=str, help='Author to search RFCs of. Give name in format: "J. Doe"')
    parser.add_argument("-i", "--init", help="Initialise the database, combine with --minimal for a \
                        database without author information", action="store_true")
    #parser.add_argument("-m", "--minimal", action="store_true", help="Use together with init ro create a minimal database without author information")
    parser.add_argument("-r", "--read", type=str, help="Read the given RFC number in the terminal")
    parser.add_argument("-t", "--title", type=str, help="Search for RFC's by title")
    parser.add_argument("-u", "--update", action="store_true", help="Update the RFC database")

    args = parser.parse_args()
    if args.author:
        find_by_author(args.author)
    elif args.title:
        find_by_title(args.title)
    elif args.init:
        init()
    elif args.read:
        read_rfc(args.read)
    elif args.update:
        update()
