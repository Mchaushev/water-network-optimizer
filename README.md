Water Network Optimizer

A Python-based web application for automated optimization of water distribution networks using EPANET, EPyT and Optuna.

Overview

Water Network Optimizer is a specialized engineering application designed to automate the hydraulic evaluation and preliminary sizing of water distribution networks.

The application combines hydraulic simulation with optimization algorithms to search for pipe diameter configurations that satisfy user-defined hydraulic criteria while minimizing the overall diameter-length index of the network.

The project was developed as a practical application of Python programming, hydraulic modelling and engineering optimization.

Main Features
Upload and process EPANET .inp network files
Read and analyze network topology and pipe properties
Perform hydraulic simulations using EPANET through EPyT
Automatically select pipe diameters from predefined diameter options
Optimize pipe diameter configurations using Optuna
Define user-specific hydraulic constraints:
Minimum pressure
Maximum pressure
Maximum velocity
Identify feasible network solutions
Rank the best feasible solutions
Generate optimized EPANET .inp files
Generate CSV reports containing optimization results
Handle cases where no feasible solution is found
Identify and export the closest infeasible solution based on normalized constraint violation
Provide a web-based user interface using Flask
Optimization Approach

The application uses Optuna to search for combinations of pipe diameters.

For each trial:

A diameter is selected for each pipe.
The corresponding EPANET network is generated.
A hydraulic simulation is performed.
Minimum and maximum pressures and maximum pipe velocity are evaluated.
The hydraulic constraints are checked.
Feasible solutions are evaluated using the network's diameter-length index.

The primary optimization objective for feasible solutions is:

Diameter-Length Index (DLI)

The index represents the combined influence of pipe diameter and pipe length and is used as a measure of the overall size of the network.

The optimization therefore aims to find a hydraulically acceptable network configuration with a lower overall DLI.

Handling Infeasible Solutions

A network may not have a feasible solution within the available diameter options and hydraulic constraints.

Instead of simply reporting that optimization failed, the application evaluates the degree of constraint violation for each infeasible trial.

The violation is normalized for each criterion and combined into a total constraint violation value.

This allows the application to identify the closest infeasible solution and provide it to the user for further engineering analysis.

Technology Stack
Programming
Python
Flask
Optuna
Hydraulic Modelling
EPANET
EPyT
Data and Reporting
CSV
EPANET .inp files
Development Tools
PyCharm
Git
GitHub
Application Architecture

The project separates the web interface from the engineering and optimization logic.

User
 │
 ▼
Flask Web Interface
 │
 ├── Network Upload
 ├── Hydraulic Criteria
 └── Optimization Settings
 │
 ▼
Optimization Engine
 │
 └── Optuna
      │
      ▼
   EPyT / EPANET
      │
      ▼
Hydraulic Results
      │
      ├── Feasible Solutions
      │      ├── Optimized .inp
      │      └── CSV Report
      │
      └── No Feasible Solution
             └── Closest Infeasible .inp
Project Structure
water-network-optimizer/
│
├── app.py
│
├── evaluation/
│   ├── diameter_options.py
│   ├── network_evaluator.py
│   ├── network_optimizer_optuna.py
│   ├── network_reader.py
│   ├── optimization_config.py
│   ├── pipe_manager.py
│   ├── quantity_report_3.py
│   ├── solution_report.py
│   └── test_optimizer.py
│
├── templates/
│   ├── index.html
│   └── results.html
│
├── static/
│   └── css/
│       └── style.css
│
└── README.md
Current Workflow

The current version provides the following workflow:

Upload EPANET network
        ↓
Review network
        ↓
Define hydraulic criteria
        ↓
Run Optuna optimization
        ↓
Evaluate hydraulic constraints
        ↓
      ┌───────────────┐
      │ Feasible?     │
      └───────┬───────┘
          Yes │ No
              │
       ┌──────┴───────┐
       ↓              ↓
Best solutions   Closest infeasible
       ↓              ↓
.INP + CSV         .INP
Engineering Background

The project is based on practical experience in water supply and sewerage infrastructure, hydraulic modelling and technical evaluation of investment projects.

The software is intended to explore how established hydraulic modelling tools can be combined with modern optimization techniques to automate repetitive engineering tasks.

The application is not intended to replace engineering judgement. Its purpose is to assist the engineer by reducing the amount of manual trial-and-error required during preliminary network sizing and evaluation.

Development Approach

The project is developed incrementally.

The initial implementation focused on:

EPANET network reading
Hydraulic simulation
Pipe diameter selection
Network evaluation

The optimization engine was subsequently extended with Optuna.

The current version introduces a Flask-based web interface, transforming the original Python optimization workflow into an interactive engineering application.

Future versions will continue to extend the application's functionality, usability and engineering capabilities.

Author

Mihail Chaushev

Water Infrastructure Engineer with experience in:

Water supply and sewerage infrastructure
Hydraulic modelling
Technical evaluation of infrastructure projects
EU-funded investment projects
Engineering design
Python-based automation and optimization

This project represents an ongoing transition from traditional engineering workflows toward software-assisted engineering and digital infrastructure tools.
