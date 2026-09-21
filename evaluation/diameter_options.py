from network_reader import read_network
from optimization_config import available_diameters


def create_diameter_options(inp_file):
    """
    Creates diameter options automatically for all pipes
    found in the EPANET input file.

    Parameters:
        inp_file:
            Path to the EPANET .inp file.

    Returns:
        Dictionary with pipe IDs as keys and the available
        diameter options as values.
    """

    pipes = read_network(inp_file)

    diameter_options = {}

    for pipe_id in pipes:
        diameter_options[pipe_id] = available_diameters.copy()

    return diameter_options


if __name__ == "__main__":

    input_file = "../networks/test_network.inp"

    diameter_options = create_diameter_options(
        input_file
    )

    print("\n")
    print("=" * 80)
    print("AUTOMATIC DIAMETER OPTIONS")
    print("=" * 80)

    for pipe_id, diameters in diameter_options.items():

        print(
            f"{pipe_id}: "
            f"{diameters}"
        )