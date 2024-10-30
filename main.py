#!/usr/bin/env python3
import bottle
import threading
from simulator import Simulator
from cpee_req_handler import patient_admission, fetch_system_state, task_simulation, patient_release, patient_replan
from database import reset_database

@bottle.route('/patient_admission', method = 'POST')
def patient_admission_handler():
    return patient_admission(simulator)

@bottle.route('/system_state', method = 'GET')
def system_state_handler():
    return fetch_system_state(simulator)

@bottle.route('/task_simulation', method = 'POST')
def task_simulation_handler():
    return task_simulation(simulator)

@bottle.route('/patient_release', method = 'POST')
def patient_release_handler():
    return patient_release(simulator)

@bottle.route('/patient_replan', method = 'POST')
def patient_replan_handler():
    return patient_replan(simulator)


#generate_patient_instance(patient_type, patient_diagnosis, arrival_time, patsourient_id)


if __name__ == '__main__':
    
    reset_database()

    simulator = Simulator()
    thread = threading.Thread(target = simulator.run)
    thread.start()
    bottle.run(host='::0', port=17779)
