import warnings
import csv
# import os

import optuna
from pipe_manager import (
    set_pipe_diameters,
    save_pipe_configuration
)
from network_evaluator import evaluate_network
from network_reader import read_network
from diameter_options import create_diameter_options
from optimization_config import (
    input_file,
    output_directory,
    criteria
)



def calculate_diameter_length_index(
        pipe_diameters,
        pipes
):
    """
    Calculates the Diameter-Length Index (DLI).

    DLI = sum(diameter * pipe length)
    """

    diameter_length_index = 0.0

    for pipe_id, diameter in pipe_diameters.items():

        length = pipes[pipe_id]["length"]

        diameter_length_index += (
            diameter * length
        )

    return diameter_length_index

def get_top_solutions(study, max_solutions=3):
    """
    Returns the best unique feasible solutions
    sorted by Diameter-Length Index (DLI).
    """

    completed_trials = [
        trial
        for trial in study.trials
        if trial.value is not None
        and trial.value != float("inf")
    ]

    completed_trials.sort(
        key=lambda trial: trial.value
    )

    unique_solutions = []
    seen_configurations = set()

    for trial in completed_trials:

        configuration = tuple(
            sorted(trial.params.items())
        )

        if configuration in seen_configurations:
            continue

        seen_configurations.add(
            configuration
        )

        unique_solutions.append(trial)

        if len(unique_solutions) >= max_solutions:
            break

    return unique_solutions

def create_optuna_csv_report(
        results,
        output_directory
):
    """
    Creates a CSV report with the Top Optuna solutions.
    """

    output_file = (
        output_directory
        + "/optuna_top_3_solutions.csv"
    )

    fieldnames = [
        "Rank",
        "Trial",
        "DLI",
        "Min Pressure",
        "Min Pressure Node",
        "Max Pressure",
        "Max Pressure Node",
        "Max Velocity",
        "Max Velocity Pipe",
        "Pressure Min OK",
        "Pressure Max OK",
        "Velocity OK",
        "Feasible",
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6"
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter=";"
        )

        writer.writeheader()

        for result in results:

            row = {
                "Rank": result["rank"],
                "Trial": result["trial"],
                "DLI": result["dli"],

                "Min Pressure": result[
                    "min_pressure"
                ],

                "Min Pressure Node": result[
                    "min_pressure_node"
                ],

                "Max Pressure": result[
                    "max_pressure"
                ],

                "Max Pressure Node": result[
                    "max_pressure_node"
                ],

                "Max Velocity": result[
                    "max_velocity"
                ],

                "Max Velocity Pipe": result[
                    "max_velocity_pipe"
                ],

                "Pressure Min OK": result[
                    "pressure_min_ok"
                ],

                "Pressure Max OK": result[
                    "pressure_max_ok"
                ],

                "Velocity OK": result[
                    "velocity_ok"
                ],

                "Feasible": result[
                    "feasible"
                ]
            }

            for pipe_id, diameter in (
                result["diameters"].items()
            ):
                row[pipe_id] = diameter

            writer.writerow(row)

    return output_file

def optimize_network(
        inp_file,
        criteria,
        n_trials=50000
):

    pipes = read_network(inp_file)

    diameter_options = create_diameter_options(
        inp_file
    )

    pipe_ids = list(
        diameter_options.keys()
    )

    def objective(trial):

        selected_diameters = {}

        for pipe_id in pipe_ids:

            selected_diameters[pipe_id] = (
                trial.suggest_categorical(
                    pipe_id,
                    diameter_options[pipe_id]
                )
            )

        d = set_pipe_diameters(
            inp_file,
            selected_diameters
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d.solveCompleteHydraulics()

        node_names = d.getNodeNameID()
        pressures = d.getNodePressure()

        junction_names = d.getNodeJunctionNameID()

        junction_indices = [
            node_names.index(name)
            for name in junction_names
        ]

        junction_pressures = (
            pressures[junction_indices]
        )

        min_pressure = junction_pressures.min()
        max_pressure = junction_pressures.max()

        velocities = d.getLinkVelocity()

        max_velocity = velocities.max()

        d.closeNetwork()

        pressure_min_ok = (
            min_pressure >=
            criteria["min_pressure"]
        )

        pressure_max_ok = (
            max_pressure <=
            criteria["max_pressure"]
        )

        velocity_ok = (
            max_velocity <=
            criteria["max_velocity"]
        )

        feasible = (
            pressure_min_ok
            and pressure_max_ok
            and velocity_ok
        )

        if not feasible:

            return float("inf")

        diameter_length_index = (
            calculate_diameter_length_index(
                selected_diameters,
                pipes
            )
        )

        return diameter_length_index

    study = optuna.create_study(
        direction="minimize"
    )

    study.optimize(
        objective,
        n_trials=n_trials
    )

    return study


if __name__ == "__main__":

    print("\n")
    print("=" * 80)
    print("OPTUNA WATER NETWORK OPTIMIZER")
    print("=" * 80)

    study = optimize_network(
        input_file,
        criteria,
        n_trials=100
    )

    top_solutions = get_top_solutions(
        study,
        max_solutions=3
    )

    results = []

    csv_file = create_optuna_csv_report(
        results,
        output_directory
    )

    print("\n")
    print("=" * 80)
    print("TOP 3 SOLUTIONS")
    print("=" * 80)



    for rank, trial in enumerate(
            top_solutions,
            start=1
    ):

        print("\n" + "-" * 80)

        print(
            f"SOLUTION #{rank}"
        )

        print(
            f"DLI: {trial.value:.0f}"
        )

        print(
            f"Trial: {trial.number}"
        )

        print("\n--- PIPE DIAMETERS ---")

        for pipe_id, diameter in (
                trial.params.items()
        ):
            print(
                f"{pipe_id}: DN{diameter}"
            )

        # Generate EPANET input file
        output_file = (
                output_directory
                + f"/optuna_solution_{rank}.inp"
        )

        save_pipe_configuration(
            input_file,
            output_file,
            trial.params
        )

        # Hydraulic evaluation
        hydraulic_result = evaluate_network(
            output_file,
            criteria
        )
        # temp_file = output_file.replace(
        #     ".inp",
        #     "_temp.inp"
        # )
        #
        # if os.path.exists(temp_file):
        #     os.remove(temp_file)

        print("\n--- HYDRAULIC RESULTS ---")

        print(
            f"Minimum pressure: "
            f"{hydraulic_result['min_pressure']:.3f} m "
            f"({hydraulic_result['min_pressure_node']})"
        )

        print(
            f"Maximum pressure: "
            f"{hydraulic_result['max_pressure']:.3f} m "
            f"({hydraulic_result['max_pressure_node']})"
        )

        print(
            f"Maximum velocity: "
            f"{hydraulic_result['max_velocity']:.3f} m/s "
            f"({hydraulic_result['max_velocity_pipe']})"
        )

        print("\n--- CRITERIA CHECK ---")

        print(
            f"Minimum pressure OK: "
            f"{hydraulic_result['pressure_min_ok']}"
        )

        print(
            f"Maximum pressure OK: "
            f"{hydraulic_result['pressure_max_ok']}"
        )

        print(
            f"Maximum velocity OK: "
            f"{hydraulic_result['velocity_ok']}"
        )

        print(
            f"FEASIBLE: "
            f"{hydraulic_result['feasible']}"
        )

        print("\nOutput file:")
        print(output_file)

        # Store results for CSV
        results.append({
            "rank": rank,
            "trial": trial.number,
            "dli": trial.value,
            "diameters": trial.params.copy(),
            "min_pressure": hydraulic_result[
                "min_pressure"
            ],
            "min_pressure_node": hydraulic_result[
                "min_pressure_node"
            ],
            "max_pressure": hydraulic_result[
                "max_pressure"
            ],
            "max_pressure_node": hydraulic_result[
                "max_pressure_node"
            ],
            "max_velocity": hydraulic_result[
                "max_velocity"
            ],
            "max_velocity_pipe": hydraulic_result[
                "max_velocity_pipe"
            ],
            "pressure_min_ok": hydraulic_result[
                "pressure_min_ok"
            ],
            "pressure_max_ok": hydraulic_result[
                "pressure_max_ok"
            ],
            "velocity_ok": hydraulic_result[
                "velocity_ok"
            ],
            "feasible": hydraulic_result[
                "feasible"
            ]
        })
    csv_file = create_optuna_csv_report(
        results,
        output_directory
    )

    print("\n--- CSV REPORT ---")
    print(
        "CSV report saved to:"
    )

    print(csv_file)