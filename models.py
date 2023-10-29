from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(400), unique=True, nullable=False)
    fullname = db.Column(db.Text, unique=False, nullable=True)
    email = db.Column(db.String(400), nullable=True)
    password = db.Column(db.String(1000), unique=False, nullable=True)
    passwordToken = db.Column(db.Text, unique=False, nullable=True)
    passwordResetTimer = db.Column(db.Integer, unique=False, nullable=True, default=-1)
    highPermissionLevel = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    isOffice = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    userData = db.Column(db.Text, unique=False, nullable=True)
    
    def __repr__(self):
        return '<User %r>' % self.username

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), unique=False, nullable=True)
    is_open = db.Column(db.Boolean, unique=False, nullable = False, default= True)
    document = db.Column(db.Text, unique=False, nullable=False) #This contains base64'ed binary images and videos in a python list.
    time = db.Column(db.Integer, unique = False) # The time the ticket was created in epoch seconds
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hidden = db.Column(db.Boolean, unique=False, default= False)
    concerns_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = True)
    base_document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable = False)
    sent = db.Column(db.Boolean, default=False)
    
    created_by = db.relationship('User', backref='tickets_created_by', foreign_keys=[created_by_id])
    concerns = db.relationship('User', backref='tickets_concerning', foreign_keys=[concerns_id])
    def __repr__(self):
        return '<Ticket %r>' % self.title

class TicketReply(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text, unique=False, nullable=False)
    document = db.Column(db.Text, unique=False, nullable=False)
    isNote = db.Column(db.Boolean, unique=False, nullable = True)
    time = db.Column(db.Integer, unique = False) # The time the ticket reply was created in epoch seconds
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    main_ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))

    created_by = db.relationship('User', backref='ticket_reply_by', foreign_keys=[created_by_id])
    main_ticket = db.relationship('Ticket', backref = 'ticket_reply_main_ticket', foreign_keys=[main_ticket_id])
    def __repr__(self):
        return '<TicketReply to %r>' % self.main_ticket

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), unique=False, nullable=False)
    fileName = db.Column(db.Text, unique=True, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fields = db.Column(db.Text, unique=False, nullable=True)
    
    created_by = db.relationship('User', backref='documents_created_by', foreign_keys=[created_by_id])

