# Hydraulic criteria

import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

input_file = os.path.join(
    BASE_DIR,
    "networks",
    "test_network.inp"
)

output_directory = os.path.join(
    BASE_DIR,
    "networks",
    "optimized"
)
criteria = {
    "min_pressure": 20.0,
    "max_pressure": 60.0,
    "max_velocity": 2.0
}

# Available diameter options for each pipe

available_diameters = [
    90,
    110,
    125,
    140,
    160,
    180,
    200,
    225,
    250,
    280,
    315
]