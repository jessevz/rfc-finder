import regex as re
import os
import requests
import subprocess

class RFC:
    def __init__(self, rfc_number, title, authors):
        self.rfc_number = rfc_number
        self.title = title
        self.authors = authors
        
    def __str__(self):
        return f"RFC Number: {self.rfc_number}\nTitle: {self.title}\nauthors: {', '.join(self.authors)}"

def parse_rfc_webpage(data, start, db):
    index = data.find(start)
    parsed_webpage =  data[index:].split("\n\n")

    for rfc in parsed_webpage:
        if "Not Issued." in rfc:
            continue
        parsed_rfc = parse_rfc(rfc)
        print(parsed_rfc)
        db.insert_RFC(parsed_rfc)

def parse_authors(rfc):
    '''
    gets data in following format when authors:
    G. Mirsky, W. Meng, T. Ao, B. Khasnabish, K. Leung, G. Mishra. November 2023. (Format: HTML, TXT, PDF, XML) (Status: PROPOSED STANDARD) (DOI: 10.17487/RFC9516)
    this function splits the data and loops by two for first name and surname
    When the last character of the surname is a ".", the names are finished

    another anoying edge case or names like "G.H Mealy" because of the dot in the middle

    But there is also a situations with an institute as author:
        Information Sciences Institute University of Southern California. August 1971. (Format: TXT, HTML) (Obsoletes RFC0207) (Updated by RFC0222) (Status: UNKNOWN) (DOI: 10.17487/RFC0212)
    '''
    names = []
    splitted = rfc.split()

    name = ""
    for i in splitted:
        name = name + " " + i

        if i[-1] == ',':
            name = name.strip()
            names.append(name[:-1])
            name = ""
        elif i[-1] == '.' and len(i) > 2 and "." not in i[:-1]: 
            name = name.strip()
            names.append(name[:-1])
            break

    return names

def clean_up_rfc(rfc):
    rfc = rfc.replace("\n", " ").replace("     ", "").replace(", Ed..", ".").replace(", Ed.", ",")
    return rfc

#Cant simply split on dot because of names like "2.0"
def parse_rfc_name(rfc):
    pattern = r'(?<=.{2,})\. '

    match = re.split(pattern, rfc)
    if match:
        name = match[0]
        return name
    else:
        print("Failed parsing: " + rfc)

    return rfc

def parse_rfc(rfc):
    rfc = clean_up_rfc(rfc) 
    index = rfc.find(" ")
    rfc_number = int(rfc[:index])
    
    current_string = rfc[index:]
    title = parse_rfc_name(current_string)

    current_string = current_string.replace(title, "")[2:]

    authors = parse_authors(current_string)

    return RFC(rfc_number, title, authors)

def read_rfc(rfc_number):
    homedir = os.path.expanduser("~")
    filename = f"{homedir}/.rfc-finder/rfc/{rfc_number}.txt"
    if not os.path.isfile(filename):
        url = f"https://www.rfc-editor.org/rfc/rfc{rfc_number}.txt"
        r = requests.get(url)
        with open(filename, "wb") as outfile:
            outfile.write(r.content)
    try:
        subprocess.run(["less", filename], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)



