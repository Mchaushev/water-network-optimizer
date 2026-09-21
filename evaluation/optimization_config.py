# Hydraulic criteria

input_file = "../networks/test_network.inp"

output_directory = "../networks/optimized"

criteria = {
    "min_pressure": 20.0,
    "max_pressure": 60.0,
    "max_velocity": 2.0
}

# Available diameter options for each pipe

available_diameters = [
    90,
    160
]
