# simpleticket main app file


# Handle Imports
from flask import Flask, session, render_template, redirect, url_for, request, abort, g, send_file
from flask_migrate import Migrate
import sqlalchemy
import hashlib

import models as m
import PDFEdit as p
import document as d

try: 
    import userconfig as config
except: 
    import config

import json, user, os, time, datetime

# prepare language files
with open("lang/"+config.LANGUAGE+".json",'r',encoding="utf-8") as langfile:
    lang = json.load(langfile)

version = "Git Error"

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simpleticket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
m.db.init_app(app)
Migrate(app, m.db, render_as_batch=True)

# make some variables available to the main script
@app.before_request
def initializeRequest():
    g.current_user = None
    g.isLoggedIn = False
    if "login" in session.keys() and session['login']:
        g.current_user = user.get_user(session['acc_id'])
        g.isLoggedIn = True

# make some variables available to the templating engine
@app.context_processor
def global_template_vars():
    return {
        "sitename": config.SITE_NAME,
        "lang": lang,
        "stversion": version,
        "current_user": g.current_user,
        "ctime": time.ctime,
        "getTime": user.getTime,
        "hasValidReply": user.hasValidReply, 
        "officeData": user.getAllOfficesData(),
    }
# set a custom 404 error page to make the web app pretty
@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404error.html'),404

# set a custom 403 error page to make the web app pretty
@app.errorhandler(403)
def accessDenied(e):
    return render_template('403error.html'),403

# set a custom 500 error page to make the web app pretty
@app.errorhandler(500)
def serverError(e):
    return render_template('500error.html'),500

# the index and home landing page. this displays all the active and closed tickets.
@app.route('/')
def home():
    if "login" in session.keys() and session['login']:
        ticket_list = []
        if g.current_user.isOffice: 
            ticket_list = list(m.Ticket.query.filter_by(concerns_id = g.current_user.id, hidden=False))
        ticket_list.extend(m.Ticket.query.filter_by(created_by_id = g.current_user.id))
        user_documents = m.Document.query.filter_by(created_by_id=g.current_user.id).all()
        return render_template('index.html', user_documents=user_documents, ticket_list = ticket_list)
    else:
        return render_template('landing.html')

# the page to view and edit tickets.
@app.route('/view/<ticketid>', methods=['GET', 'POST'])
def viewTicket(ticketid):
    ticket = m.Ticket.query.filter_by(id = ticketid).first()
    if ticket == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if request.method == 'POST':
            ticket.assigned_to_id = request.form["new-assignee-id"]
            m.db.session.commit()
        ticket_replies = m.TicketReply.query.filter_by(main_ticket = ticket)
        return render_template('ticket-view.html', ticket = ticket, replies = ticket_replies)
    else:
        abort(403)

@app.route('/view/<ticketid>/close')
def closeTicket(ticketid):
    ticket = m.Ticket.query.filter_by(id = ticketid).first()
    if ticket == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.id == ticket.created_by_id or g.current_user.highPermissionLevel:
            ticket.is_open = False
            m.db.session.commit()
            return redirect(url_for('viewTicket', ticketid = ticketid))
        else:
            abort(403)
    else:
        abort(403)

@app.route('/view/<ticketid>/reopen')
def reopenTicket(ticketid):
    ticket = m.Ticket.query.filter_by(id = ticketid).first()
    if ticket == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.id == ticket.created_by_id or g.current_user.highPermissionLevel:
            ticket.is_open = True
            m.db.session.commit()
            return redirect(url_for('viewTicket', ticketid = ticketid))
        else:
            abort(403)
    else:
        abort(403)

@app.route('/view/<ticketid>/hide')
def hideTicket(ticketid):
    ticket = m.Ticket.query.filter_by(id = ticketid).first()
    if ticket == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.id == ticket.created_by_id or g.current_user.highPermissionLevel:
            ticket.hidden = True
            m.db.session.commit()
            return redirect(url_for('viewTicket', ticketid = ticketid))
        else:
            abort(403)
    else:
        abort(403)

@app.route('/view/<ticketid>/unhide')
def unhideTicket(ticketid):
    ticket = m.Ticket.query.filter_by(id = ticketid).first()
    if ticket == None:
        abort(404)
    if "login" in session.keys() and session['login']:
        if g.current_user.id == ticket.created_by_id or g.current_user.highPermissionLevel:
            ticket.hidden = False
            m.db.session.commit()
            return redirect(url_for('viewTicket', ticketid = ticketid))
        else:
            abort(403)
    else:
        abort(403)

@app.route('/view/<ticketid>/reply', methods=['POST'])
def createTicketReply(ticketid):
    if "login" in session.keys() and session['login']:
        if request.method == 'POST':
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '': 
                if request.form.get('action') == "SaveNote":
                    user.create_ticket_reply(request.form["reply-text"], None, g.current_user, ticketid, isNote=True)
                else:
                    user.create_ticket_reply(request.form["reply-text"], None, g.current_user, ticketid)
            else:
                upload_path = 'static/document_data/reply/' + str(g.current_user.id) + '/'
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                file_path = os.path.join(upload_path, hashlib.md5(pdf_file.read()).hexdigest()+".pdf")
                pdf_file.seek(0)
                pdf_file.save(file_path)
                if request.form.get('action') == "SaveNote":
                    user.create_ticket_reply(request.form["reply-text"], None, g.current_user, ticketid, isNote=True, document = file_path)
                else:
                    user.create_ticket_reply(request.form["reply-text"], None, g.current_user, ticketid, document = file_path)
            return redirect(url_for('viewTicket', ticketid = ticketid))
        return redirect(url_for('viewTicket', ticketid = ticketid))
    else:
        abort(403)

@app.route('/view/<ticketid>/delete')
def deleteTicket(ticketid):
    if "login" in session.keys() and session['login']:
        try:
            ticket = m.Ticket.query.get(ticketid)
            if ticket:
                if ticket.created_by_id == g.current_user.id or g.current_user.highPermissionLevel:
                    m.db.session.delete(ticket)
                    m.db.session.commit()
                    return redirect(url_for('home'))
                else:
                    abort(403)
        except Exception as e:
            m.db.session.rollback()
            return False, str(e)
        return redirect(url_for('home'))

# the about page. this shows the current software version and some general information about simpleticket.
@app.route('/about')
def about():
    return render_template('about.html')

# the login page. this allows a user to authenticate to enable them to create and edit tickets.
@app.route('/login', methods=['GET', 'POST'])
def login(message = None):
    if request.method == 'POST':
        username = str.lower(request.form["login"]) # make sure the login string is only in lowercase
        password = request.form["password"]
        acc = user.verify_login(username, password)
        if acc:
            session['login'] = True
            session['acc_id'] = acc.id
            return redirect(url_for('home'))
        else: 
            message = lang["login-error"]
    return render_template('user-login.html', message = message)

# provide a logout url. we dont want users to get stuck logged in :)
@app.route('/logout')
def logout():
    session['login'] = False
    session['acc_id'] = None
    return redirect(url_for('home'))

# the password reset page to enable the users to reset their own password, provided they know their own email address.
@app.route('/pwreset', methods=['GET', 'POST'])
def resetPW():
    message = None
    if request.method == 'POST':
        message = lang['password-reset-form-message']
        userobj = m.User.query.filter_by(email = request.form["email"]).first()
        if userobj == None:
            message = lang['user-not-found-error']
            return render_template('user-password-reset.html', message = message)
        user.resetpw(userobj)
        return render_template('user-password-reset.html', message = message)
    return render_template('user-password-reset.html', message = message)

@app.route('/add-admin', methods=['GET', 'POST'])
def addAdmin():
    if os.path.exists(config.CREATE_ADMIN_FILE) or ("login" in session.keys() and session['login'] and g.current_user.highPermissionLevel):
        if request.method == 'POST':
            try:
                user.create_user(str.lower(request.form["username"]), request.form["fullname"], request.form["email"], user.hashPassword(request.form["password"]), highPermissionLevel=True)
            except sqlalchemy.exc.ç:
                return render_template('user-signup.html', perms = lang["high-perms"], message = lang["user-create-error"])
            return redirect(url_for('login'))
        return render_template('user-signup.html', perms = lang["high-perms"])
    else:
        abort(403)

@app.route('/add-office', methods=['GET', 'POST'])
def addOffice():
    if "login" in session.keys() and session['login'] and g.current_user.highPermissionLevel:
        if request.method == 'POST':
            try:
                user.create_user(str.lower(request.form["username"]), request.form["fullname"], request.form["email"], user.hashPassword(request.form["password"]), 
                                 highPermissionLevel=False, isOffice = True)
            except sqlalchemy.exc.IntegrityError:
                return render_template('user-signup.html', perms = "Office", message = lang["user-create-error"])
            return redirect(url_for('login'))
        return render_template('user-signup.html', perms = "Office")
    else:
        abort(403)
        
@app.route('/add-user', methods=['GET', 'POST'])      
def addUser():
    if request.method == 'POST':
        try:
            user.create_user(str.lower(request.form["username"]), request.form["fullname"], request.form["email"], user.hashPassword(request.form["password"]), highPermissionLevel=False)
        except sqlalchemy.exc.IntegrityError:
            return render_template('user-signup.html', perms = lang["low-perms"], message = lang["user-create-error"])
        return redirect(url_for('login'))
    return render_template('user-signup.html', perms = lang["low-perms"])
    


@app.route('/account-settings', methods=['GET', 'POST'])
def changeSettings():
    if "login" in session.keys() and session['login']:
        image_src = ""
        if request.method == 'POST':
            try:
                user.modify_user_password(g.current_user.id, user.hashPassword(request.form["password"]))
            except sqlalchemy.exc.IntegrityError:
                return render_template('account-settings.html', message = lang["user-modify-error"], userData = user.get_user_data(g.current_user.id))
            return redirect(url_for('home'))
        return render_template('account-settings.html', userData = user.get_user_data(g.current_user.id))
    else:
        abort(403)


@app.route('/account-settings-data', methods=['POST'])
def updateUserData():
    if "login" in session.keys() and session['login'] :
        if user.verify_password(g.current_user.id, request.form["passwordValidation"]):
            myForm = request.form.to_dict()
            myForm["passwordValidationOptional"] = ''
            try:
                if g.current_user.isOffice: 
                    user.set_office_data_validate(g.current_user.id, myForm)
                    this_user = m.User.query.get(g.current_user.id)
                    this_user.fullname = myForm["fullname"]
                    m.db.session.commit()
                else: 
                    user.set_user_data_validate(g.current_user.id, myForm)
                    this_user = m.User.query.get(g.current_user.id)
                    this_user.fullname = myForm["fullname"]
                    m.db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                return render_template('account-settings.html', message = lang["user-modify-error"])
            except KeyError as e:
                print (e)
            except ValueError as e:
                 return render_template('account-settings.html', message = lang["user-modify-invalid"] + " " + str(e), userData = request.form)
            return redirect(url_for('home'))
        else:
            return render_template('account-settings.html', message = lang["user-modify-error"], userData = request.form)
    else:
        abort(403)

@app.route('/admin-settings', methods=['GET', 'POST'])
def adminUserSettigs():
    if "login" in session.keys() and session['login'] and g.current_user.highPermissionLevel:
        if request.method == 'POST':
            try:
                user.modify_user_password(user.get_userid(request.form["username"]), user.hashPassword(request.form["password"]))
            except sqlalchemy.exc.IntegrityError:
                return render_template('admin-settings.html', message = lang["user-modify-error"])
            return redirect(url_for('home'))
        return render_template('admin-settings.html')
    else:
        abort(403)

@app.route('/store', methods=['GET', 'POST'])
def storeformular():
    if "login" in session.keys() and session['login']:
        if request.method == 'POST':
            try:    
                pdf_file = request.files['pdf_file']
                if pdf_file.filename == '': 
                    return 'Keine ausgewählte Datei'
                
                upload_path = 'static/document_data/' + str(g.current_user.id) + '/'
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                file_path = os.path.join(upload_path, hashlib.md5(pdf_file.read()).hexdigest()+".pdf")
                pdf_file.seek(0)
                pdf_file.save(file_path)
                
                formId = d.create_document("Unnamed Form", file_path, g.current_user, None)
                print("created by: ", g.current_user, g.current_user.fullname)
                return redirect(url_for('formSetup', formId = formId))
            except sqlalchemy.exc.IntegrityError:
                m.db.session.rollback()
                return render_template('store-pdf.html', message = lang["doc-already-exist"])
        return render_template('store-pdf.html')
    else:
        abort(403)

@app.route('/formSetup/<formId>', methods=['GET', 'POST'])
def formSetup(formId):
    if "login" in session.keys() and session['login']:
        document = m.Document.query.filter_by(id = formId).first()
        if document.created_by_id == g.current_user.id: 
            if request.method == 'POST':
                document.title = request.form['formtitle']
                document.fields = request.form['field-pos']
                m.db.session.commit()
                return redirect(url_for('home'))
            else:
                return render_template('edit-fields.html', document = document)
        else:
            abort(403)
    else:
        abort(403)
    
        

@app.route('/office/<useroffice>')
def viewOffice(useroffice):
    try:
        offices = user.getOfficeData(useroffice)[0]    
        officeID = offices["id"]
        documents = m.Document.query.filter_by(created_by_id=officeID).all()
        if offices == None:
            abort(404)
        if "login" in session.keys() and session['login']:
            return render_template('office.html', office = offices, documents=documents)
        else:
            abort(403)
    except ValueError as e:
            return render_template('404error.html', message = lang["non-existend-office"])

@app.route('/download/<int:document_id>')
def download_document(document_id):
    document = m.Document.query.get(document_id)
    filename = document.title + ".pdf"; 
    file_path = document.fileName;  
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/download_ticket/<int:ticket_id>')
def download_ticket(ticket_id):
    if "login" in session.keys() and session['login']:
        ticket = m.Ticket.query.get(ticket_id)
        if ticket.created_by_id == g.current_user.id or g.current_user.highPermissionLevel:
            base_document = m.Document.query.get(ticket.base_document_id)
            filename = base_document.fileName + base_document.title + "_filled.pdf"
            return send_file(filename, as_attachment=True, download_name=filename)
        else:
            abort(403)
    else:
        abort(403)

@app.route('/download_reply/<int:reply_id>')
def download_ticketReply(reply_id):
    if "login" in session.keys() and session['login']:
        ticketReply = m.TicketReply.query.get(reply_id)
        print(m.TicketReply.query.all())
        if ticketReply.main_ticket.created_by_id == g.current_user.id or g.current_user.highPermissionLevel:
            return send_file(ticketReply.document, as_attachment=True, download_name=ticketReply.document.split("/")[-1])
        else:
            abort(403)
    else:
        abort(403)

@app.route('/fill/<id>')
def fill_form(id):
    if "login" in session.keys() and session['login']:
        try:
            user_data = json.loads(g.current_user.userData)
        except TypeError:
            return redirect(url_for('changeSettings'))
        document = m.Document.query.get(id)
        filename, datastring = d.fill_and_download_document(document, user_data)
        user.create_ticket(document.title, json.dumps(datastring), id, g.current_user.id, document.created_by_id)
        return send_file(filename, as_attachment=True, download_name=filename)
    abort(403)

@app.route('/delete/<int:document_id>')
def delete_document(document_id):
    if "login" in session.keys() and session['login']:
        try:
            form_to_delete = m.Document.query.get(document_id)
            if form_to_delete:
                if form_to_delete.created_by_id == g.current_user.id or g.current_user.highPermissionLevel:
                    m.db.session.delete(form_to_delete)
                    m.db.session.commit()
                    return redirect(url_for('home'))
                else:
                    abort(403)
        except Exception as e:
            m.db.session.rollback()
            return False, str(e)
        return redirect(url_for('home'))