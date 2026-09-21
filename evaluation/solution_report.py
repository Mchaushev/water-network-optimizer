import csv


def print_solution_report(
        solution,
        rank,
        output_file
):
    """
    Prints a detailed report for one optimized solution.
    """

    print("\n")
    print("=" * 80)
    print(f"OPTIMIZED SOLUTION #{rank}")
    print("=" * 80)

    # --------------------------------------------------
    # EPANET FILE
    # --------------------------------------------------

    print(
        f"\nEPANET file:"
        f"\n{output_file}"
    )

    # --------------------------------------------------
    # PIPE DIAMETERS
    # --------------------------------------------------

    print("\n--- PIPE DIAMETERS ---")

    pipe_ids = [
        key
        for key in solution
        if key.startswith("P")
    ]

    for pipe_id in pipe_ids:

        print(
            f"{pipe_id}: "
            f"DN{solution[pipe_id]}"
        )

    # --------------------------------------------------
    # QUANTITIES
    # --------------------------------------------------

    print("\n--- PIPE QUANTITIES ---")

    quantities = solution["quantities"]

    for diameter in sorted(quantities):

        print(
            f"DN{diameter}: "
            f"{quantities[diameter]:.2f} m"
        )

    print(
        f"\nTotal pipe length: "
        f"{solution['total_length']:.2f} m"
    )

    # --------------------------------------------------
    # OPTIMIZATION
    # --------------------------------------------------

    print("\n--- OPTIMIZATION ---")

    print(
        f"Diameter-Length Index: "
        f"{solution['diameter_length_index']:.0f}"
    )

    # --------------------------------------------------
    # HYDRAULIC RESULTS
    # --------------------------------------------------

    print("\n--- HYDRAULIC RESULTS ---")

    print(
        f"Minimum pressure: "
        f"{solution['min_pressure']:.2f} m "
        f"({solution['min_pressure_node']})"
    )

    print(
        f"Maximum pressure: "
        f"{solution['max_pressure']:.2f} m "
        f"({solution['max_pressure_node']})"
    )

    print(
        f"Maximum velocity: "
        f"{solution['max_velocity']:.2f} m/s "
        f"({solution['max_velocity_pipe']})"
    )

    # --------------------------------------------------
    # CRITERIA
    # --------------------------------------------------

    print("\n--- CRITERIA CHECK ---")

    print(
        f"Minimum pressure: "
        f"{'OK' if solution['pressure_min_ok'] else 'NOT OK'}"
    )

    print(
        f"Maximum pressure: "
        f"{'OK' if solution['pressure_max_ok'] else 'NOT OK'}"
    )

    print(
        f"Maximum velocity: "
        f"{'OK' if solution['velocity_ok'] else 'NOT OK'}"
    )

    print(
        f"\nSTATUS: "
        f"{'FEASIBLE' if solution['feasible'] else 'NOT FEASIBLE'}"
    )


def create_csv_report(
        solutions,
        output_file
):
    """
    Creates a CSV report containing the selected solutions.

    Parameters:
        solutions:
            List of optimized solutions.

        output_file:
            Path to the CSV file.
    """

    if not solutions:
        return

    # --------------------------------------------------
    # Determine pipe IDs
    # --------------------------------------------------

    pipe_ids = [
        key
        for key in solutions[0]
        if key.startswith("P")
    ]

    pipe_ids.sort()

    # --------------------------------------------------
    # Determine diameters
    # --------------------------------------------------

    all_diameters = set()

    for solution in solutions:

        all_diameters.update(
            solution["quantities"].keys()
        )

    all_diameters = sorted(all_diameters)

    # --------------------------------------------------
    # CSV columns
    # --------------------------------------------------

    fieldnames = [
        "Rank",
        "Combination",
        "Diameter-Length Index",
        "Min Pressure (m)",
        "Min Pressure Node",
        "Max Pressure (m)",
        "Max Pressure Node",
        "Max Velocity (m/s)",
        "Max Velocity Pipe"
    ]

    # Pipe diameters
    for pipe_id in pipe_ids:
        fieldnames.append(
            pipe_id
        )

    # Quantities
    for diameter in all_diameters:
        fieldnames.append(
            f"DN{diameter} Length (m)"
        )

    fieldnames.extend([
        "Total Length (m)",
        "EPANET File"
    ])

    # --------------------------------------------------
    # Write CSV
    # --------------------------------------------------

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            delimiter=";"
        )

        writer.writeheader()

        for rank, solution in enumerate(
            solutions,
            start=1
        ):

            row = {
                "Rank": rank,

                "Combination":
                    solution["combination"],

                "Diameter-Length Index":
                    round(
                        solution["diameter_length_index"],
                        2
                    ),

                "Min Pressure (m)":
                    round(
                        solution["min_pressure"],
                        3
                    ),

                "Min Pressure Node":
                    solution["min_pressure_node"],

                "Max Pressure (m)":
                    round(
                        solution["max_pressure"],
                        3
                    ),

                "Max Pressure Node":
                    solution["max_pressure_node"],

                "Max Velocity (m/s)":
                    round(
                        solution["max_velocity"],
                        3
                    ),

                "Max Velocity Pipe":
                    solution["max_velocity_pipe"],

                "Total Length (m)":
                    round(
                        solution["total_length"],
                        2
                    ),

                "EPANET File":
                    solution.get(
                        "output_file",
                        ""
                    )
            }

            # Pipe diameters
            for pipe_id in pipe_ids:

                row[pipe_id] = (
                    solution[pipe_id]
                )

            # Quantities by diameter
            for diameter in all_diameters:

                row[
                    f"DN{diameter} Length (m)"
                ] = round(
                    solution["quantities"].get(
                        diameter,
                        0.0
                    ),
                    2
                )

            writer.writerow(row)
