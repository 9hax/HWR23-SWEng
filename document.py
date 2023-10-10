from simpleticket import m

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

# def get_field_positions(form_string):
    field_data = {}

    lines = form_string.split('\n')

    for line in lines:
        parts = line.strip().split('=')
        if len(parts) == 2:
            name = parts[0].strip()
            values = parts[1].strip().split(';')
            if len(values) == 2:
                x_position = int(values[0].strip())
                y_position = int(values[1].strip())
                field_data[name] = {
                    "X-Position": x_position,
                    "Y-Position": y_position
                }

    return field_data