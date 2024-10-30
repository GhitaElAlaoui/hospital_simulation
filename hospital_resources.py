import sqlite3

#function to connect to the database
def connect(db='hospital.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    return connection, cursor

#function to increment resource count
def increment(resource, incrementby=1):
    connection, cursor = connect()
    cursor.execute('''
        UPDATE resources
        SET count = count + ?
        WHERE resource = ?
    ''', (incrementby, resource))
    connection.commit()
    connection.close()

#functinon to decrement resource count
def decrement(resource, decrementby=1):
    connection, cursor = connect()
    cursor.execute('''
        UPDATE resources
        SET count = count - ?
        WHERE resource = ?
    ''', (decrementby, resource))
    connection.commit()
    connection.close()

#function to get resource type for specific task
def resource_type(task, patient_type = None):
    resource = None
    if task == "ER_Treatment":
        resource = "ER personnel"
    elif task == "Intake":
        resource = "Intake personnel"
    elif task == "Surgery":
        resource = "Operating rooms"
    elif task == "Nursing":
        if patient_type == "A":
            resource = "Nursing beds A"
        elif patient_type == "B":
            resource = "Nursing beds B"
    return resource
    
#function to get countn of a resource
def getcount(resource):
    connection, cursor = connect()
    cursor.execute('''
        SELECT count FROM resources
        WHERE resource = ?
    ''', (resource,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    else:
        return None

#function to reset database (initial resources count)
def reset():
    resources = [
        ('ER personnel', 9),
        ('Intake personnel', 4),
        ('Operating rooms', 5),
        ('Nursing beds A', 30),
        ('Nursing beds B', 40)
    ]
    connection, cursor = connect()
    for resource, count in resources:
        cursor.execute('''
            UPDATE resources
            SET count = ?
            WHERE resource = ?
        ''', (count, resource))
    connection.commit()
    connection.close()

def check_availability_admission(patient_type):
    if patient_type == 'EM':
        print(f"Resource count: {getcount('ER personnel')}")
        return getcount('ER personnel') > 0
    else:
        return getcount('Intake') > 0

#Function to check availability of a resource for a defined task
def check_availability(task, patient_type = None):
    if task == "ER_Treatment":
        return getcount('ER personnel') > 0
    elif task == "Intake":
        return getcount('Intake personnel') > 0
    elif task == "Surgery":
        return getcount('Operating rooms') > 0
    elif task == "Nursing":
        if patient_type == "A":
            return getcount('Nursing beds A') > 0
        elif patient_type == "B":
            return getcount('Nursing beds B') > 0
