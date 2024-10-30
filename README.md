# Praktikum SS24
**Advanced Practical Course - Message Correlation and Inter-Instance/Process Communication in Process-Aware Information Systems**

## Project Structure
- **main.py**: Main entry point; starts the web server and initializes the simulator.
- **simulator.py**: Core simulation logic, handling scheduling and processing of patient events. Event types include:
  - Generating patients
  - Admitting patients
  - Starting/completing tasks
  - Queuing
  - Releasing or replanning patients
- **cpee_req_handler.py**: Manages REST requests for controlling patient flow.
- **patient_req.py**: Provides utilities for patient generation, including a function for creating CPEE patient instances.
- **hospital_resources.py**: Manages hospital resource allocation and availability. Functions include:
  - Incrementing and decrementing resource counts
  - Checking availability for tasks
  - Resetting resources to initial levels
- **database.py**: Initializes and resets the SQLite database, specifically the resources table, which tracks counts for various hospital resources (e.g., ER personnel, intake personnel, nursing beds).
- **patient_config.json**: Defines patient types, arrival rates, diagnoses, and task requirements for the simulation, including:
  - Arrival rates
  - Task duration distributions
  - Complication probabilities

## CPEE Endpoints
- **POST /patient_admission** - Admit a patient.
- **GET /system_state** - Fetch current system state.
- **POST /task_simulation** - Simulate a patient task.
- **POST /patient_release** - Release a patient.
- **POST /patient_replan** - Replan a patient.

## Getting Started

To start the application, run:
```bash
python main.py

