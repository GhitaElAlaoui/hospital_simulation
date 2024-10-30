#!/usr/bin/env python3
import json
import bottle
import uuid
import time
import random
import requests
import patient_req 
import hospital_resources
from queue import PriorityQueue
from collections import defaultdict
import threading
from enum import Enum, auto
import time

class EventType(Enum):
    GENERATE_PATIENT = auto()
    ADMIT_PATIENT = auto()
    START_TASK = auto()
    QUEUE_PATIENT = auto()
    COMPLETE_TASK = auto()
    RELEASE_PATIENT = auto()
    REPLAN_PATIENT = auto()

class SimulationEvent:
    def __init__(self, type, patient_id, patient_type, patient_diagnosis, start, end= None, task = None, resource = None, callback_url = None , json_content = None):
        self.type = type
        self.start = start 
        self.end = end
        self.task =  task
        self.resource = resource
        self.patient_id = patient_id 
        self.patient_type = patient_type
        self.patient_diagnosis = patient_diagnosis
        self.callback_url = callback_url
        self.json_content = json_content
        
        
    def __lt__(self, other):
        return (self.start) < (other.start)

    
    def __str__(self):
    	return str(self.type) + "\t(" + str(round(self.start, 2)) + ")\t" + str(self.patient_id) + "," + str(self.resource)


class Simulator:
    def __init__(self):
        self.running_time = 10
        self.newid = 1
        self.events = PriorityQueue()
        self.patient_queues = defaultdict(PriorityQueue)
        self.current_patients = 0
        self.now = 0.0
        self.pending = 0
        self.pstate = {}
        self.callback_condition = threading.Condition()
        patients = patient_req.generate_patients(3)
        self.schedule_patient_generation(patients)
        self.CALLBACK_HEADER = {
                'content-type': 'application/json',
                'CPEE-CALLBACK': 'true'
                }
        
    def system_state(self):
        return [
        {
            "cid": patient_id, 
            "task": p["task"], 
            "start": p["start"], 
            "info": p["info"], 
            "wait": p["wait"]
        } 
        for patient_id, p in self.pstate.items()
    ]
    

    def schedule_patient_generation(self, patients):
        for p in patients: 
            arrival_time = p["arrival_time"]
            patient_type = p["type"]
            patient_diagnosis = p["diagnosis"]
            self.events.put((arrival_time, SimulationEvent(type = EventType.GENERATE_PATIENT, 
                                             start = arrival_time, 
                                             patient_id = None, 
                                             patient_type = patient_type,
                                             patient_diagnosis = patient_diagnosis)))  
        print(list(self.events.queue))

    def wait_for_callbacks(self):
            with self.callback_condition:
                print(f"Waiting for callbacks. Current pending: {self.pending}")
                while self.pending > 0:
                    self.callback_condition.wait()
                print("All callbacks processed.")

    def print_current_event_queue(self):
        # Extract and print the events with their string representations
        event_list = [(event[0], str(event[1])) for event in self.events.queue]
        print("Current event queue:", event_list)
    
    """
    def run(self):
        while (self.events.qsize() > 0 or self.current_patients > 0):
            print(f"Checking queue size: {self.events.qsize()}, Current pending: {self.pending}, Current patients: {self.current_patients}")
            while self.pending > 0:
                time.sleep(0.001)
            (self.now, event) = self.events.get()
            print(f"Processing event: {event.type} at time {self.now}")
            self.print_current_event_queue()
            self.process(event)
            print("POST PROCESS:")
            self.print_current_event_queue()

        print("\n-------------------\nSIMULATION FINISHED\n-------------------\n")

    
    def run(self):
        while True:
            print(f"Checking queue size: {self.events.qsize()}, Current patients: {self.current_patients}")
            self.wait_for_callbacks()
            if self.events.qsize() > 0 or self.current_patients > 0:
                (self.now, event) = self.events.get()  # Process next event
                print(f"Processing event: {event.type} at time {self.now}")
                self.process(event)
                #self.wait_for_callbacks()
            else:
                time.sleep(0.1)

            if self.events.qsize() == 0 and self.current_patients == 0:
                print("No more events or patients. Exiting loop.")
                break
   """
    
    def run(self):
    # Main simulation loop
        while True: 
        #while self.now <= self.running_time:
        #while (self.events.qsize() > 0) or (self.current_patients > 0):
            #self.wait_for_callbacks()
            print(f"Current event queue size: {self.events.qsize()}")
            (self.now, event) = self.events.get()  # Process next event
            print(f"Processing event: {event.type} at time {self.now}")
            print(f"STATE: {self.pstate}")
            self.process(event)
            print(f"Event processed. Current simulation time: {self.now}")
            #self.print_current_event_queue()  # Check the event queue state after processing 
            #print(f"STATE: {self.pstate}")
        print("\n-------------------\nSIMULATION FINISHED\n-------------------\n")
    

    """def run(self):
        #Main simulation loop
        while (self.events.qsize() > 0) or (self.current_patients > 0):
            self.wait_for_callbacks()
            self.now, event = self.events.get()
            self.process(event)
            #self.print_current_event_queue()
            #self.wait_for_callbacks()
            
        print("\n-------------------\nSIMULATION FINISHED\n-------------------\n")
    """
    def process(self, event):
        print(f"Running for event of type: {event.type}")
        if event.type == EventType.GENERATE_PATIENT:
            self.pending += 1
            try:
                patient_req.generate_patient_instance(
                    patient_type = event.patient_type, 
                    patient_diagnosis = event.patient_diagnosis, 
                    arrival_time = event.start, 
                    patient_id = event.patient_id
                    )
                print(f"Patient generated with diagnosis {event.patient_diagnosis}, and arrival time {event.start}")
            finally:
                #with self.callback_condition:
                self.pending -= 1
                   # self.callback_condition.notify_all()
        
        elif event.type == EventType.ADMIT_PATIENT:
            self.current_patients += 1
            print(f"Patient {event.patient_id} admitted")

        elif event.type == EventType.START_TASK:
            patient_id = event.patient_id
            patient_diagnosis = event.patient_diagnosis
            task = event.task
            start = event.start
            task_duration = patient_req.get_task_duration(patient_diagnosis)
            need_surgery = patient_req.need_surgery(patient_diagnosis)
            finish_time = start + task_duration
            self.pstate[patient_id] = {"task": task, "start": start, "info": {"diagnosis": patient_diagnosis}, "wait": False}
            self.events.put((finish_time, SimulationEvent(type = EventType.COMPLETE_TASK, 
                                                    start = start, 
                                                    end = finish_time,
                                                    task = task,
                                                    patient_id = patient_id,
                                                    patient_diagnosis = patient_diagnosis,
                                                    need_surgery = need_surgery)))

        elif event.type == EventType.QUEUE_PATIENT:
            self.pstate[event.patient_id] = {"task": event.task, "start": event.start, "info": {"diagnosis": event.patient_diagnosis}, "wait": True}
            print(f"Patient {event.patient_id} queued.")

        elif event.type == EventType.COMPLETE_TASK:
            
            print(f"COMPLETE_TASK {event.task} event triggered.")
            del self.pstate[event.patient_id]
            hospital_resources.increment(event.resource)
            print(f"Resource {event.resource} released")
            print(f"EVENT: {event.task}, PATIENT_TYPE: {event.patient_type}")
            queue = self.patient_queues[hospital_resources.resource_type(event.task, event.patient_type)]
            if not queue.empty():
                priority, patient_id, patient_type, patient_diagnosis, start, resource, callback_url = self.queue.get()
                self.events.put((event.end, SimulationEvent(type=EventType.START_TASK, 
                                                  start = event.end, 
                                                  resource = resource, 
                                                  callback_url = callback_url,
                                                  patient_id = patient_id, 
                                                  patient_type = patient_type,
                                                  patient_diagnosis = patient_diagnosis)))
            print(event.json_content)
            #self.pending += 1
            try:
                print(f"Sending callback to {event.callback_url} with data: {event.json_content}")
                response = requests.put(event.callback_url, headers=self.CALLBACK_HEADER, json=event.json_content)
                response.raise_for_status()  # This will raise an exception for bad responses
            except requests.exceptions.RequestException as e:
                print(f"Callback failed: {e}")
           # requests.put(event.callback_url, headers = self.HEADER, json = event.json_content)
            #self.pending -= 1

        elif event.type == EventType.RELEASE_PATIENT:
            self.current_patients -= 1
            print(f"Patient {event.patient_id} released.")

        elif event.type == EventType.REPLAN_PATIENT:
            print(f"Patient{event.patient_id} replanned.")
            self.current_patients -= 1
            self.events.put((event.end, SimulationEvent(type = EventType.GENERATE_PATIENT, 
                                                    start = event.end, 
                                                    end = event.end,
                                                    task = event.task,
                                                    patient_id = event.patient_id,
                                                    patient_type = event.patient_type,
                                                    patient_diagnosis=event.patient_diagnosis)))
