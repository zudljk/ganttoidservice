import sqlite3

# SQLite database configuration
DATABASE = 'ganttoidservice.db'

def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db(app):
    db = getattr(app, '_database', None)
    if db is None:
        db = app._database = sqlite3.connect(DATABASE)
    return db


def write_to_db(app, entity, fields, values):
    db = get_db(app)
    cursor = db.cursor()
    fieldlist = ", ".join(fields)
    valuelist = ', '.join(['?' for _ in range(len(fields))])
    cursor.execute(f"INSERT INTO {entity} ({fieldlist} VALUES ({valuelist}))", tuple(values))
    db.commit()


def update_to_db(app, entity, updates, key_field, key_value):
    db = get_db(app)
    cursor = db.cursor()
    set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
    values = updates.values()[:]
    values.append(key_value)
    cursor.execute(f"UPDATE {entity} SET {set_clause} WHERE {key_field} = ?", (values))
    db.commit()
    

def read_from_db(app, entity, return_fields, key_field, key_value):
    db = get_db(app)
    cursor = db.cursor()
    return_string = ', '.join(return_fields)
    return cursor.execute(f"SELECT {return_string} FROM {entity} WHERE {key_field} = ?", (key_value)).fetchone()
      