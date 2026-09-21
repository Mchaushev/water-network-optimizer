from epyt import epanet


def create_quantity_report(inp_file, pipe_diameters):
    """
    Creates a quantity report for a selected pipe diameter configuration.

    Parameters:
        inp_file:
            Path to the EPANET .inp file.

        pipe_diameters:
            Dictionary containing pipe IDs and selected diameters.

    Returns:
        Dictionary containing:
            - quantities by diameter
            - total pipe length
            - diameter-length index
    """

    d = epanet(inp_file)

    pipe_names = d.getLinkNameID()
    pipe_lengths = d.getLinkLength()

    quantities = {}

    diameter_length_index = 0.0

    for pipe_id, diameter in pipe_diameters.items():

        pipe_index = pipe_names.index(pipe_id)

        length = pipe_lengths[pipe_index]

        if diameter not in quantities:
            quantities[diameter] = 0.0

        quantities[diameter] += length

        diameter_length_index += diameter * length

    total_length = sum(
        quantities.values()
    )

    d.closeNetwork()

    return {
        "quantities": quantities,
        "total_length": total_length,
        "diameter_length_index": diameter_length_index
    }


if __name__ == "__main__":

    input_file = "../networks/test_network.inp"

    selected_diameters = {
        "P1": 160,
        "P2": 90,
        "P3": 90,
        "P4": 90,
        "P5": 90,
        "P6": 90
    }

    result = create_quantity_report(
        input_file,
        selected_diameters
    )

    print("\n")
    print("=" * 60)
    print("PIPE QUANTITY REPORT")
    print("=" * 60)

    print(
        f"\n{'Diameter':>10} | "
        f"{'Length':>12}"
    )

    print("-" * 60)

    for diameter in sorted(
        result["quantities"]
    ):

        length = result["quantities"][diameter]

        print(
            f"DN{diameter:>7} | "
            f"{length:>9.2f} m"
        )

    print("-" * 60)

    print(
        f"{'TOTAL':>10} | "
        f"{result['total_length']:>9.2f} m"
    )

    print(
        f"\nDiameter-Length Index: "
        f"{result['diameter_length_index']:.0f}"
    )