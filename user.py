import bcrypt
import smtpconfig
import json
import time
import datetime
import random
import string
import re
from simpleticket import m

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
     
    modified_user = get_user(userid)
    modified_user.userData = json.dumps(newUserData)
    m.db.session.commit()

def set_office_data_validate(userid, userData):
    newUserData={}
    if validateName(userData["officeName"]):
        newUserData["officeName"] =  userData["officeName"]
    else: 
        raise ValueError("Invalid office name")
    if validateAddress(userData["addressOffice"]):
        newUserData["addressOffice"] =  userData["addressOffice"]
    else: 
        raise ValueError("Invalid address")
    
    if validateOpeningAndClosingTime(userData["openingTime"]):
        newUserData["openingTime"] =  userData["openingTime"]
    else: 
        raise ValueError("Invalid opening time")
    
    if validateOpeningAndClosingTime(userData["closingTime"]):
        newUserData["closingTime"] =  userData["closingTime"]
    else: 
        raise ValueError("Invalid closing time")
    
    modified_user = get_user(userid)
    modified_user.userData = json.dumps(newUserData)
    m.db.session.commit()
    
def set_optional_user_data_validate(userid, optionalData, nameOfOptional, dataOfOptional):
    newOptionalUserData={}
    newOptionalUserData[nameOfOptional] =  optionalData[dataOfOptional]

    modified_user = get_user(userid)
    modified_user.optionalData = json.dumps(newOptionalUserData)
    m.db.session.commit()
    
def validateName(name):
    if " " not in name:
        return False
    if name.__len__() < 3:
        return False
    return True
    
def validateDateofbirth(dateofbirth):
    pattern = "^(19\d{2}|20\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
    return  re.match(pattern,dateofbirth)

def validateAddress(address):
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
