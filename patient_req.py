import json
import requests 
import random 

#Function to generate a CPEE instance
def generate_instance(init_data):
    header_url = "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Ghita_ElAlaouiTalibi.dir/hospital.xml"
    post_url = "https://cpee.org/flow/start/url/"
    behavior =  "fork_running"
    #behavior = "fork_ready"
    data = {
            "behavior": behavior, 
            "url": header_url,
            "init": json.dumps(init_data)
            }
    response = requests.post(post_url, data = data)
    if response.status_code == 200:
        print("successful")
        print("Response:", response.text)
    else:
        print("failed", response.status_code)
        print("Response:", response.text)

#Function to generate a patient (CPEE instance) with defined type, diagnosis, arrival_time and patient id if given.
def generate_patient_instance(patient_type, patient_diagnosis, arrival_time, patient_id = None):
    if patient_id is None:
        init_data = {"patient_type": patient_type, "patient_diagnosis": patient_diagnosis, "arrival_time": arrival_time}
    else: 
        init_data = {"patient_id": patient_id, "patient_type": patient_type, "patient_diagnosis": patient_diagnosis, "arrival_time": arrival_time}
    generate_instance(init_data)

#Function to load json patients' arrival information
def load_patient_config():
    with open('patient_config.json', 'r') as file:
        return json.load(file)["patients"]

#Function to assign a patient diagnosis based on given probabilities      
def diagnosis(patient_type):
    if patient_type == "A":
        diagnosis = random.choices(["A1", "A2", "A3", "A4"], [0.5, 0.25, 0.125, 0.125])[0]
    elif patient_type == "B":
        diagnosis = random.choices(["B1", "B2", "B3", "B4"], [0.5, 0.25, 0.125, 0.125])[0]
    elif patient_type =="EM":
        diagnosis = "EM"
    else:  
        raise Exception("Invalid patient type")
    return diagnosis

def distribution(distr):
    distribution_type = distr["distribution"]
    params = distr["params"]
    if distribution_type == "uniform":
        return random.uniform(*params)
    elif distribution_type == "exponential":
        return random.expovariate(params[0])
    elif distribution_type == "normal":
        return random.gauss(params[0], params[1])
    else: 
        return ValueError(f"Unknown distribution type.")

#Function to get (from the patient config file) the operation or nursing time distribution for a patient depending on the diagnosis
def get_distribution(task, diagnosis):
    patients_config = load_patient_config()
    for p in patients_config:
        for d in p["diagnoses"]:
            if d["diagnosis"] == diagnosis:
                if task == "Surgery":
                    return distribution(d["op_duration"])
                elif task == "Nursing":
                    return distribution(d["nursing_duration"])

#Function to get task (ER_Treatment, Intake, Surgery, Nursing) duration based on defined distribution for a specific patient diagnosis
def get_task_duration(task, diagnosis):
    if task == "ER_Treatment":
        return max(0.0, random.gauss(2, 0.5))
    elif task == "Intake":
        return max(0.0, random.gauss(1,0.125))
    elif task == "Surgery":
        return max(0.0, get_distribution(task, diagnosis))
    elif task == "Nursing":
        return max(0.0, get_distribution(task, diagnosis))
    else:
        raise ValueError(f"Invalid task.")

#Function to generate a list of initial patients list based on arrival rates defined
def generate_patients(total_time):
    patients_config = load_patient_config()
    patients = []
    current_time = 0.0
    step = 1.0
    while current_time < total_time:
        for p in patients_config:
            patient_type = p["type"]
            arrival_rate = distribution(p["arrival_rate"])
            arrival_time = current_time + arrival_rate
            patient_type = p["type"]
            patient_diagnosis = diagnosis(patient_type)
            patients.append({
                "arrival_time": arrival_time,
                "type": patient_type,
                "diagnosis": patient_diagnosis
            })
        current_time += step

    return patients

#Functinon to get if a patient needs surgery
def need_surgery(diagnosis):
    patients_config = load_patient_config()
    for p in patients_config:
        for d in p["diagnoses"]:
            if d["diagnosis"] == diagnosis:
                if d["op_duration"] is None:
                    return False
                else:
                    return True
    raise ValueError(f"Diagnosis {diagnosis} not found in the patient configuration.")

#Functionn to get if a patient has complications
def get_complications(diagnosis):
    patients_config = load_patient_config()
    for p in patients_config:
        for d in p["diagnoses"]:
            if ["diagnosis"] == diagnosis:
                proba = d["complications_proba"]
                if proba is not None:
                    return "True" if random.random() < proba else "False"
                # If no probability is defined, assume no complications
                return "False"
