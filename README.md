# Praktikum SS24
Advanced Practical Course - Message Correlation and Inter-Instance/Process Communication in Process Aware Information Systems

# Project Structure
main.py: Main entry point; starts the web server and initializes the simulator.
simulator.py: Core simulation logic, scheduling and processing patient events. Event types include generating patients, admitting patients, starting/completing tasks, queuing, and releasing or replanning patients.
cpee_req_handler.py: Handles REST requests for managing patient flow.
patient_req.py: Utilities for patient generation including function for cpee patient instance generation.
hospital_resources.py: Manages hospital resource allocation and availability. It includes functions for incrementing and decrementing resource counts, checking availability for different tasks, and resetting resources to initial levels.
database.py: Initializes and resets the SQLite database, specifically the resources table, which keeps track of counts for various hospital resources (e.g., ER personnel, intake personnel, nursing beds).
patient_config.json: Defines patient types, arrival rates, diagnoses, and task requirements for the simulation, setting parameters like arrival rate, task duration distributions, and complication probabilities.

# CPEE Endpoints
POST /patient_admission - Admit a patient.
GET /system_state - Fetch current system state.
POST /task_simulation - Simulate a patient task.
POST /patient_release - Release a patient.
POST /patient_replan - Replan a patient.

# Getting started

Run main.py

