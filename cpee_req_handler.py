import bottle
import json
from simulator import EventType, SimulationEvent
from hospital_resources import resource_type, check_availability, decrement
import patient_req
import requests


def patient_admission(simulator):

    print(f"Functionality: {bottle.request.headers['CPEE-LABEL']}")
    patient_id  = bottle.request.forms.patient_id
    print(f"Patient ID: {patient_id}")
    patient_type = bottle.request.forms.patient_type
    patient_diagnosis = bottle.request.forms.patient_diagnosis
    print(f"Patient Type: {patient_type}, diagnosis: {patient_diagnosis}")
    admission_time = float(bottle.request.forms.arrival_time)
    if not patient_id:
        patient_id = simulator.newid
        simulator.newid += 1
        print(f"New patient ID: {patient_id}")
        
    if patient_type == "EM":
        next_task = "ER_Treatment"
    else:
        next_task = "Intake"
    #check if intake/ ER resources are available
    available = check_availability(next_task)

    #For non-emergency patients, check if surgery/nursing queues>2
    if patient_type != "EM": 
        surgery_queue = simulator.patient_queues[resource_type("Surgery")]
        nursing_queue = simulator.patient_queues[resource_type("Nursing", "A" if patient_type == "A" else "B")]
        if surgery_queue.qsize() > 2 or nursing_queue.qsize() > 2:
            available = "False"
    
    simulator.events.put((admission_time, SimulationEvent(type=EventType.ADMIT_PATIENT, 
                                            start = admission_time, 
                                            end = admission_time,
                                            patient_id = patient_id,
                                            patient_type = patient_type,
                                            patient_diagnosis = patient_diagnosis)))
    
    print("Current event queue:", simulator.print_current_event_queue())
    
    return bottle.HTTPResponse(
        json.dumps({"patient_id": patient_id, "resources_available": available}),
        status = 200,
        headers = {'content-type': 'application/json'}
    )
    
def fetch_system_state(simulator):
    return bottle.HTTPResponse(
            json.dumps({"state": simulator.system_state()}),
            status=200,
            headers = {'content-type': 'application/json'}
            )
    
def task_simulation(simulator): #er treatment, intake, surgery or nursing
    
    task = bottle.request.headers['CPEE-LABEL']
    print(f"Functionality: {task}")
    patient_id = bottle.request.forms.patient_id
    patient_type = bottle.request.forms.patient_type
    patient_diagnosis = bottle.request.forms.patient_diagnosis
    resource = resource_type(task, patient_type)
    start_time = float(bottle.request.forms.arrival_time)
    print(f"TASK {task}, PATIENT DIAGNOSIS: {patient_diagnosis}")
    task_duration = patient_req.get_task_duration(task,patient_diagnosis)
    callback_url = bottle.request.headers['CPEE-CALLBACK'] 
    print(f"Duration: {task_duration}")
    finish_time = start_time + task_duration 
    available = check_availability(task, patient_type) 
    need_surgery = patient_req.need_surgery(patient_diagnosis)
    complications = patient_req.get_complications(patient_diagnosis)
    if task == "Intake":
        print(f"Patient needs surgery: {need_surgery}")
    if task == "Nursing":
        print(f"Patient has complications: {complications}")

    json_content = {"patient_diagnosis": patient_diagnosis, "finish_time": finish_time, "need_surgery": need_surgery, "complications": complications}
    
    if available:
        print(f"Resources for {task} available for patient {patient_id} ")
        decrement(resource) #resource assigned
        simulator.pstate[patient_id] = {"task": task, "start": start_time, "info": {"diagnosis": patient_diagnosis}, "wait": False}

        simulator.events.put((finish_time, SimulationEvent(type = EventType.COMPLETE_TASK, 
                                          start = start_time,
                                          end = finish_time, 
                                          task = task,
                                          resource = resource,
                                          patient_id = patient_id,
                                          patient_type = patient_type,
                                          patient_diagnosis = patient_diagnosis,
                                          callback_url = callback_url,
                                          json_content = json_content)))
        
        print(f"JSON CONTENT: {json_content}")
    else: 
        print(f"Resources {resource} for {task} not available --> patient queued")
        if patient_type == "EM":
            priority = 0
        else: 
            priority = 1
        #queue patient
        simulator.patient_queues[resource].put((priority, patient_id, patient_type, patient_diagnosis, start_time, resource, callback_url))
        simulator.events.put((start_time, SimulationEvent(type=EventType.QUEUE_PATIENT, 
                                              start = start_time, 
                                              resource = resource, 
                                              callback_url = callback_url, 
                                              patient_id = patient_id, 
                                              patient_type = patient_type,
                                              patient_diagnosis = patient_diagnosis)))
        
    return bottle.HTTPResponse(
        json.dumps({'message':'Request accepted, process async'}),
        status = 202,
        headers={'content-type': 'application/json','CPEE-CALLBACK': 'true'}
    )
    
def patient_release(simulator):
    patient_id = bottle.request.forms.patient_id
    patient_type = bottle.request.forms.patient_type
    patient_diagnosis = bottle.request.forms.patient_diagnosis
    release_time = float(bottle.request.forms.release_time)
    simulator.events.put((release_time, SimulationEvent(type=EventType.RELEASE_PATIENT, 
                                   start = release_time, 
                                   end = release_time,
                                   patient_id = patient_id,
                                   patient_type = patient_type,
                                   patient_diagnosis = patient_diagnosis)))
    return bottle.HTTPResponse(
        json.dumps({"patient_id": patient_id}),
        status = 200,
        headers = {'content_type': 'applicaction/json'}
    )
    
def patient_replan(simulator):
    print("Patient Replan")
