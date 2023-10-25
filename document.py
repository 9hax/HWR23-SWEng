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
    except:
        raise ValueError("Invalid Field positions! Please use the graphical editor.")

    return positions

def fill_and_download_document(document_id, user_data):
    document = m.Document.query.get(document_id)
    filename = document.title + "_filled.pdf"
    filepath = document.fileName
    field_positions = json.loads(document.fields)

    pdf_data = []
    for index, page in enumerate(field_positions):
        pdf_data[index] = []
        for field_name in page:
            pdf_data.append(user_data.get(field_name))        

    try:
        with open(filepath, "rb") as document_file:
            content = document_file.read()
        with open('temp.pdf', "wb") as temp_file:
            temp_file.write(content)

    except FileNotFoundError:
        print("Die Datei wurde nicht gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {str(e)}")

    p.addText('temp.pdf', filename, [pdf_data])
    os.remove('temp.pdf')

    return filename

