from simpleticket import m, p
import os, json
from pathlib import Path as pa
from flask import send_file

try:
    import userconfig as config
except:
    import config

def create_document(title, filename, created_by, fields):
    new_document = m.Document()
    new_document.title = title
    new_document.fileName = filename
    new_document.created_by = created_by
    new_document.fields = fields
    m.db.session.add(new_document)
    m.db.session.commit()
    m.db.session.refresh(new_document)
    return new_document.id

def delete_document(document_id):
    try:
        form_to_delete = m.Document.query.get(document_id)

        if form_to_delete:
            m.db.session.delete(form_to_delete)
            m.db.session.commit()
            return True, "Formular erfolgreich gelöscht"
        else:
            return False, "Formular nicht gefunden"

    except Exception as e:
        m.db.session.rollback()
        return False, str(e)

def get_field_positions(input_string):
    try:
        positions = json.loads(input_string)
        # if this fails, the input is not a valid field position list and cannot be used.
        # this does not actually validate that the field position list is in a valid and correct format.
        # if this seems dangerous, that's because it is. Please ignore thise and look for bugs somewhere else. 
        # I don't actually excpect anyone to spoof this. why would anyone? please don't. 
        # you should not be able to access any user data through this anyways. 
        # if you do anyway, please let me know at http://host1.9hax.net/❤ thanks <3
    except:
        raise ValueError("Invalid Field positions! Please use the graphical editor.")

    return positions

def fill_and_download_document(document, user_data):
    filepath = document.fileName
    filename = filepath + document.title + "_filled.pdf"
    field_positions = json.loads(document.fields)

    pages = []
    for page in field_positions:
        modifications = []
        for modification in page:
            modifications.append({'x':modification['x'], 'y':modification['y'], 'text':user_data[modification['text']]})
        pages.append(modifications)


    try:
        with open(filepath, "rb") as document_file:
            content = document_file.read()
        with open(filepath+'.temp.pdf', "wb") as temp_file:
            temp_file.write(content)

    except FileNotFoundError:
        print("Die Datei wurde nicht gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {str(e)}")

    p.addText(filepath+'.temp.pdf', filename, pages)
    os.remove(filepath+'.temp.pdf')

    return filename, pages

