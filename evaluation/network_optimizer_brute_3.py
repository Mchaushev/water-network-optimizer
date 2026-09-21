from itertools import product
import os
import warnings

from pipe_manager import (
    set_pipe_diameters,
    save_pipe_configuration
)

from quantity_report_3 import create_quantity_report
from solution_report import (
    print_solution_report,
    create_csv_report
)

from optimization_config import (
    input_file,
    output_directory,
    criteria
)

from diameter_options import create_diameter_options


def optimize_network(
        inp_file,
        diameter_options,
        criteria
):
    """
    Tests all possible pipe diameter combinations.

    Only hydraulically feasible solutions are retained.

    For each feasible solution:
        - hydraulic results are stored
        - pipe quantities are calculated
        - diameter-length index is calculated

    The solutions are later sorted by the
    diameter-length index.
    """

    pipe_ids = list(diameter_options.keys())

    diameter_combinations = product(
        *(diameter_options[pipe_id] for pipe_id in pipe_ids)
    )

    results = []

    combination_number = 0

    total_combinations = 1

    for options in diameter_options.values():
        total_combinations *= len(options)

    for combination in diameter_combinations:

        combination_number += 1

        selected_diameters = dict(
            zip(pipe_ids, combination)
        )

        print(
            f"Testing combination "
            f"{combination_number}/{total_combinations}..."
        )

        # --------------------------------------------------
        # Create hydraulic model with selected diameters
        # --------------------------------------------------

        d = set_pipe_diameters(
            inp_file,
            selected_diameters
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d.solveCompleteHydraulics()

        # --------------------------------------------------
        # NODE RESULTS
        # --------------------------------------------------

        node_names = d.getNodeNameID()
        pressures = d.getNodePressure()

        junction_names = d.getNodeJunctionNameID()

        junction_indices = [
            node_names.index(name)
            for name in junction_names
        ]

        junction_pressures = pressures[
            junction_indices
        ]

        min_pressure = junction_pressures.min()

        min_pressure_index = (
            junction_pressures.argmin()
        )

        min_pressure_node = (
            junction_names[min_pressure_index]
        )

        max_pressure = junction_pressures.max()

        max_pressure_index = (
            junction_pressures.argmax()
        )

        max_pressure_node = (
            junction_names[max_pressure_index]
        )

        # --------------------------------------------------
        # PIPE RESULTS
        # --------------------------------------------------

        velocities = d.getLinkVelocity()

        max_velocity = velocities.max()

        max_velocity_index = (
            velocities.argmax()
        )

        pipe_names = d.getLinkNameID()

        max_velocity_pipe = (
            pipe_names[max_velocity_index]
        )

        # --------------------------------------------------
        # CRITERIA
        # --------------------------------------------------

        pressure_min_ok = (
            min_pressure >= criteria["min_pressure"]
        )

        pressure_max_ok = (
            max_pressure <= criteria["max_pressure"]
        )

        velocity_ok = (
            max_velocity <= criteria["max_velocity"]
        )

        feasible = (
            pressure_min_ok
            and pressure_max_ok
            and velocity_ok
        )

        # --------------------------------------------------
        # Basic result
        # --------------------------------------------------

        result = {
            "combination": combination_number,

            **selected_diameters,

            "min_pressure": min_pressure,
            "min_pressure_node": min_pressure_node,

            "max_pressure": max_pressure,
            "max_pressure_node": max_pressure_node,

            "max_velocity": max_velocity,
            "max_velocity_pipe": max_velocity_pipe,

            "pressure_min_ok": pressure_min_ok,
            "pressure_max_ok": pressure_max_ok,
            "velocity_ok": velocity_ok,

            "feasible": feasible
        }

        d.closeNetwork()

        # --------------------------------------------------
        # Quantity report ONLY for feasible solutions
        # --------------------------------------------------

        if feasible:

            quantity_result = create_quantity_report(
                inp_file,
                selected_diameters
            )
            print("DEBUG quantity_result:")
            print(quantity_result)

            result["quantities"] = (
                quantity_result["quantities"]
            )

            result["total_length"] = (
                quantity_result["total_length"]
            )

            result["diameter_length_index"] = (
                quantity_result["diameter_length_index"]
            )

        results.append(result)

    return results


def save_top_solutions(
        inp_file,
        results,
        output_directory,
        number_of_solutions=3
):
    """
    Saves the best feasible solutions as EPANET .inp files.

    Solutions are sorted by diameter-length index.
    """

    feasible_results = [
        result
        for result in results
        if result["feasible"]
    ]

    if not feasible_results:
        return []

    # Sort by diameter-length index
    ranked_results = sorted(
        feasible_results,
        key=lambda x: x["diameter_length_index"]
    )

    top_results = ranked_results[
        :number_of_solutions
    ]

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    for rank, result in enumerate(
        top_results,
        start=1
    ):

        output_file = os.path.join(
            output_directory,
            f"solution_{rank:02d}.inp"
        )

        pipe_diameters = {
            pipe_id: result[pipe_id]
            for pipe_id in results_pipe_ids
        }

        save_pipe_configuration(
            inp_file,
            output_file,
            pipe_diameters
        )

        result["rank"] = rank
        result["output_file"] = output_file

        print_solution_report(
            result,
            rank,
            output_file
        )

    return top_results


if __name__ == "__main__":

    # Used by save_top_solutions()
    diameter_options = create_diameter_options(
        input_file
    )

    results_pipe_ids = list(
        diameter_options.keys()
    )

    # --------------------------------------------------
    # RUN OPTIMIZATION
    # --------------------------------------------------

    results = optimize_network(
        input_file,
        diameter_options,
        criteria
    )

    # --------------------------------------------------
    # FEASIBLE RESULTS
    # --------------------------------------------------

    feasible_results = [
        result
        for result in results
        if result["feasible"]
    ]

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    print("\n")
    print("=" * 100)
    print("BRUTE-FORCE OPTIMIZATION SUMMARY")
    print("=" * 100)

    print(
        f"Total combinations tested: "
        f"{len(results)}"
    )

    print(
        f"Feasible combinations: "
        f"{len(feasible_results)}"
    )

    # --------------------------------------------------
    # TOP 3
    # --------------------------------------------------

    if feasible_results:

        ranked_results = sorted(
            feasible_results,
            key=lambda x: x["diameter_length_index"]
        )

        top_results = ranked_results[:3]

        print("\n")
        print("=" * 100)
        print("TOP 3 FEASIBLE SOLUTIONS")
        print("=" * 100)

        print(
            f"{'Rank':>5} | "
            f"{'Comb.':>6} | "
            f"{'DLI':>12} | "
            f"{'Min P':>8} | "
            f"{'Max P':>8} | "
            f"{'Max V':>8}"
        )

        print("-" * 100)

        for rank, result in enumerate(
            top_results,
            start=1
        ):

            print(
                f"{rank:>5} | "
                f"{result['combination']:>6} | "
                f"{result['diameter_length_index']:>12.0f} | "
                f"{result['min_pressure']:>6.2f} m | "
                f"{result['max_pressure']:>6.2f} m | "
                f"{result['max_velocity']:>6.2f} m/s"
            )

            print(
                f"       "
                f"P1={result['P1']}  "
                f"P2={result['P2']}  "
                f"P3={result['P3']}  "
                f"P4={result['P4']}  "
                f"P5={result['P5']}  "
                f"P6={result['P6']}"
            )

            print(
                "       Quantities: ",
                end=""
            )

            for diameter in sorted(
                result["quantities"]
            ):

                print(
                    f"DN{diameter}="
                    f"{result['quantities'][diameter]:.2f} m  ",
                    end=""
                )

            print()

            print(
                f"       Total length: "
                f"{result['total_length']:.2f} m"
            )

        # --------------------------------------------------
        # SAVE TOP 3 AS INP
        # --------------------------------------------------

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        print("\n")
        print("=" * 100)
        print("SAVING TOP 3 SOLUTIONS")
        print("=" * 100)

        for rank, result in enumerate(
            top_results,
            start=1
        ):
            csv_file = os.path.join(
                output_directory,
                "top_3_solutions.csv"
            )

            create_csv_report(
                top_results,
                csv_file
            )

            print(
                f"\nCSV report saved to:"
                f"\n{csv_file}"
            )

            output_file = os.path.join(
                output_directory,
                f"solution_{rank:02d}.inp"
            )

            pipe_diameters = {
                pipe_id: result[pipe_id]
                for pipe_id in results_pipe_ids
            }

            save_pipe_configuration(
                input_file,
                output_file,
                pipe_diameters
            )
            result["output_file"] = output_file

            print_solution_report(
                result,
                rank,
                output_file
            )

            print(
                f"Solution {rank}: "
                f"{output_file}"
            )

    else:

        print("\n")
        print("=" * 100)
        print("NO FEASIBLE COMBINATIONS")
        print("=" * 100)

