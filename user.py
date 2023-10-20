import bcrypt
import smtpconfig
import json
import time
import datetime
import random
import string
import re
import sqlite3
import base64
from simpleticket import m
from datetime import datetime


try:
    import userconfig as config
except:
    import config

# prepare language files

with open("lang/"+config.LANGUAGE+".json",'r',encoding="utf-8") as langfile:
    lang = json.load(langfile)

def resetpw(user):
    newPassword = ''.join(random.choices(string.ascii_uppercase + string.digits, k = random.randint(20,30)))
    user.password = hashPassword(newPassword)
    m.db.session.commit()   
    sendmail(user.email, lang["password-reset-mail"].replace("%PW%", newPassword), lang["password-reset"]+" | "+config.SITE_NAME)
    del(newPassword)

def verify_login(u, p):
    potential_user = m.User.query.filter_by(username=u.lower()).first()
    if potential_user:
        if bcrypt.checkpw(p.encode('utf-8'), potential_user.password.encode('utf-8')):
            return potential_user
    return False

def verify_password(uid, p):
    potential_user = get_user(uid)
    if potential_user:
        if bcrypt.checkpw(p.encode('utf-8'), potential_user.password.encode('utf-8')):
            return True
    return False

def hashPassword(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode()

def get_userid(username):
    return m.User.query.filter_by(username = username).first().id

def get_user(userid):
    return m.User.query.get(userid)

def get_user_data(userid):
    data = m.User.query.get(userid).userData
    return json.loads(data if data else "{}" )

def set_user_data_validate(userid, userData):
    newUserData={}
    if validateName(userData["fullname"]):
        newUserData["fullname"] =  userData["fullname"]
    else: 
        raise ValueError("Invalid fullname")
    
    if validateDateofbirth(userData["dateofbirth"]):
        newUserData["dateofbirth"] =  userData["dateofbirth"]
    else: 
        raise ValueError("Invalid dateofbirth")
    
    if validateAddress(userData["address"]):
        newUserData["address"] =  userData["address"]
    else: 
        raise ValueError("Invalid address")
    
    taxnumber= userData["taxnumber"]
    taxnumber = taxnumber.replace(" ","")

    if validateTaxnumber(taxnumber):
        newUserData["taxnumber"] =  taxnumber
    else: 
        raise ValueError("Invalid taxnumber")

    if validateTaxclass(userData["taxclass"]):
        newUserData["taxclass"] =  userData["taxclass"]
    else: 
        raise ValueError("Invalid taxclass")
    
    if validateGender(userData["gender"]):
        newUserData["gender"] =  userData["gender"]
    else: 
        raise ValueError("Invalid gender")
    
    if validateEmployer(userData["employer"]):
        newUserData["employer"] =  userData["employer"]
    else: 
        raise ValueError("Invalid employer")
    
    
    if validateImageName(userData["imageName"]):
        newUserData["imageName"] =  userData["imageName"]
    else: 
        raise ValueError("Invalid file type")
    
    if validateImageBase64(userData["base64Txt"]):
        newUserData["base64Txt"] =  userData["base64Txt"]
    else: 
        raise ValueError("Invalid Base 64 Txt")
    

   
    modified_user = get_user(userid)
    modified_user.userData = json.dumps(newUserData)
    m.db.session.commit()

def set_office_data_validate(officeid, userData):
    newOfficeData={}
    if validateName(userData["officeName"]):
        newOfficeData["officeName"] =  userData["officeName"]
    else: 
        raise ValueError("Invalid name")
    
    if validateAddress(userData["adressOffice"]):
        newOfficeData["adressOffice"] =  userData["adressOffice"]
    else: 
        raise ValueError("Invalid address")
    
    
    opening_time = datetime.strptime(userData["openingTime"], "%H:%M")
    closing_time = datetime.strptime(userData["closingTime"], "%H:%M")
    
    if validateTime(userData["openingTime"]) and opening_time<closing_time:
        newOfficeData["openingTime"] =  userData["openingTime"]
    else: 
        raise ValueError("Invalid time")
    
    if validateTime(userData["closingTime"]) and opening_time<closing_time:
        newOfficeData["closingTime"] =  userData["closingTime"]
    else: 
        raise ValueError("Invalid time")
        
    if validateName(userData["contactPersonName"]):
        newOfficeData["contactPersonName"] =  userData["contactPersonName"]
    else: 
        raise ValueError("Invalid name")
    
    if validateEmail(userData["contactPersonEmail"]):
        newOfficeData["contactPersonEmail"] =  userData["contactPersonEmail"]
    else: 
        raise ValueError("Invalid email")
    
    if validateNumber(userData["contactPersonNumber"]):
        newOfficeData["contactPersonNumber"] =  userData["contactPersonNumber"]
    else: 
        raise ValueError("Invalid number")
    print(newOfficeData)
     
    modified_user = get_user(officeid)
    modified_user.userData = json.dumps(newOfficeData)
    m.db.session.commit()

def validateName(name:str):
    if " " not in name:
        return False
    if name.__len__() < 3:
        return False
    return True

def validateImageName(imagePath):
    if imagePath is None or imagePath == "":
        return True  # Akzeptieren, wenn imagePath leer oder None ist
    
    imageDataExtensions = [".png", ".jpeg", ".jpg"]
    for extension in imageDataExtensions:
        if imagePath.endswith(extension):
            return True
    
    return False 

def validateImageBase64(base64):
    return True
    
def validateDateofbirth(dateofbirth):
    pattern = "^(19\d{2}|20\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
    return  re.match(pattern,dateofbirth)

def validateAddress(address):
    if " " not in address:
        return False
    if not any(char.isdigit() for char in address):
        return False
    return True


def validateTime(time):
    pattern = '^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
    return  re.match(pattern,time)

def validateEmail(email):
    if "@" in email:
        return True
    else: return False

def validateNumber(number):
    if not number.isdigit():
        print(number)
        return False
    print(number)

    return True

def validateTaxnumber(taxnumber):
    try: 
        number = int(taxnumber)
    except: 
        return False
    
    if taxnumber.__len__() != 11:
        return False
    return True

def validateTaxclass(taxclass):
    if taxclass not in ("1", "2", "3", "4", "5"):
        return False
    if taxclass.__len__() != 1:
        return False
    return True

def validateGender(gender):
    validoptions = ["gender-male","gender-female","gender-queer","gender-no-selection"]
    if gender in validoptions:
        return True
    return False

def validateEmployer(employer):
    return True

def validateOpeningAndClosingTime(time):
    timePattern = "^(0\d|1\d|2[0-3]):([0-5]\d)$"
    return re.match(timePattern, time)

def validateInputDocument(document_file:str):
    trimmed_document_file = document_file.strip()
    if trimmed_document_file == "" :
        return False
    return True

def validateDocumentName(name:str):
    trimmed_name = name.strip()
    if trimmed_name == "":
        return False
    return True

def create_ticket(title, text, media, created_by, assigned_to):
    new_ticket = m.Ticket()
    new_ticket.title = title
    new_ticket.is_open = True
    new_ticket.text = text
    new_ticket.media = media
    new_ticket.time = time.time()
    new_ticket.created_by = created_by
    new_ticket.assigned_to = assigned_to
    m.db.session.add(new_ticket)
    m.db.session.commit()

def create_ticket_reply(text, media, created_by, main_ticket_id, isNote = False):
    new_ticket = m.TicketReply()
    new_ticket.text = text
    new_ticket.media = media
    new_ticket.isNote = isNote
    new_ticket.time = time.time()
    new_ticket.created_by = created_by
    new_ticket.main_ticket_id = main_ticket_id
    m.db.session.add(new_ticket)
    m.db.session.commit()

def create_user(username, fullname, email, hashedPassword, passwordResetTimer = -1, highPermissionLevel = 0, isOffice = False):
    new_user = m.User()
    new_user.username = username.lower()
    new_user.fullname = fullname
    new_user.email = email
    new_user.password = hashedPassword
    new_user.passwordResetTimer = passwordResetTimer
    new_user.highPermissionLevel = highPermissionLevel
    new_user.isOffice = isOffice
    m.db.session.add(new_user)
    m.db.session.commit()

def modify_user_password(userid, newPasswordHash):
    modified_user = get_user(userid)
    modified_user.password = newPasswordHash
    m.db.session.commit()
    
def sendmail(address, htmlcontent, subject):
    import smtplib, ssl
    mailstring = "From: "+smtpconfig.SMTP_USER+"\nTo: "+address+"\nSubject: "+subject+"\n\n"+htmlcontent+"\n"
    ssl_context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtpconfig.SMTP_SERVER, smtpconfig.SMTP_PORT, context=ssl_context) as smtpserver:
        smtpserver.login(smtpconfig.SMTP_USER, smtpconfig.SMTP_PASSWORD)
        smtpserver.sendmail(smtpconfig.SMTP_USER, address, mailstring)

def getTime(timestamp):
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime(config.TIMEFORMAT)
    except:
        return "Invalid time"

def hasValidReply(ticketid):
    ticketReplyList = m.TicketReply.query.filter_by(main_ticket_id = ticketid).all()
    for reply in ticketReplyList:
        if m.User.query.filter_by(id = reply.created_by_id).first().highPermissionLevel:
            return True
    return False

def convertToBase64(imagePath):
    print(base64.b64encode(imagePath.encode()).decode())
    return base64.b64encode(imagePath.encode()).decode()

def getAllOfficesData():
    officeList = m.User.query.filter_by(isOffice = True).all()
    officeData = []
    
    for office in officeList: 
        try:         
            d = json.loads(office.userData)
            d["username"] = office.username
            d["id"] = office.id
            officeData.append(d)
        except: 
            print("OfficeData for", office, "is empty! Error while creating global template Var.")
    return officeData

def getOfficeData(username):
    office = m.User.query.filter_by(username = username).first()
    officeData = []
    
    if office is None:
        raise ValueError("Invalid office")
    else:
        d = json.loads(office.userData)
        d["username"] = office.username
        d["id"] = office.id
        officeData.append(d)
    return officeData

def getDocumentsNames(officeid):
    documents = m.Ticket.query.filter_by(created_by_id = officeid).all()
    documentsListNames = []
    for document in documents:
        title = json.dumps(document.title)
        documentsListNames.append(title)
    return documentsListNames

def verify_file(document_name, document_file):
    if  not validateDocumentName(document_name): 
        raise ValueError("Invalid Document Name")
    
    if not validateInputDocument(document_file): 
        raise ValueError("Empty file")
   
