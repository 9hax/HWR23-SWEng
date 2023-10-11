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
    attributes = input_string.split(';')
    field_positions = {}

    for attribute in attributes:
        key, positions = attribute.split('=')
        x, y = positions.split(',')
        
        field_positions[key + '-x'] = x
        field_positions[key + '-y'] = y

    return field_positions

def fill_and_download_document(document_id, user_data):
    document = m.Document.query.get(document_id)
    filename = document.title + "_filled.pdf"
    filepath = document.fileName
    field_positions = json.loads(document.fields)

    #debugging
    field_positions.get('fullname-x')
    field_positions.get('dateofbirth-x')
    field_positions.get('address-x')
    field_positions.get('taxclass-x')
    field_positions.get('taxnumber-x')
    field_positions.get('gender-x')
    field_positions.get('employer-x')

    pdf_data = [
        {'text': user_data.get('fullname'), 'x': int(field_positions.get('fullname-x')), 'y': int(field_positions.get('fullname-y'))},
        {'text': user_data.get('dateofbirth'), 'x': int(field_positions.get('dateofbirth-x')), 'y': int(field_positions.get('dateofbirth-y'))},
        {'text': user_data.get('address'), 'x': int(field_positions.get('address-x')), 'y': int(field_positions.get('address-y'))},
        {'text': user_data.get('taxnumber'), 'x': int(field_positions.get('taxnumber-x')), 'y': int(field_positions.get('taxnumber-y'))},
        {'text': user_data.get('taxclass'), 'x': int(field_positions.get('taxclass-x')), 'y': int(field_positions.get('taxclass-y'))},
        {'text': user_data.get('gender'), 'x': int(field_positions.get('gender-x')), 'y': int(field_positions.get('gender-y'))},
        {'text': user_data.get('employer'), 'x': int(field_positions.get('employer-x')), 'y': int(field_positions.get('employer-y'))}
    ]
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

