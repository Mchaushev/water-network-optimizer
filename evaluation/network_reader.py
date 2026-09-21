from epyt import epanet


def read_network(inp_file):
    """
    Reads an EPANET .inp file and extracts information
    about all pipes in the network.

    Parameters:
        inp_file:
            Path to the EPANET .inp file.

    Returns:
        Dictionary containing information about the pipes.
    """

    d = epanet(inp_file)

    pipe_names = d.getLinkNameID()
    pipe_lengths = d.getLinkLength()
    pipe_diameters = d.getLinkDiameter()
    pipe_roughness = d.getLinkRoughnessCoeff()

    link_nodes = d.getLinkNodesIndex()
    node_names = d.getNodeNameID()

    pipes = {}

    for i, pipe_id in enumerate(pipe_names):

        start_node_index = link_nodes[i][0]
        end_node_index = link_nodes[i][1]

        # EPANET uses 1-based node indices
        start_node = node_names[start_node_index - 1]
        end_node = node_names[end_node_index - 1]

        pipes[pipe_id] = {
            "start_node": start_node,
            "end_node": end_node,
            "length": pipe_lengths[i],
            "diameter": pipe_diameters[i],
            "roughness": pipe_roughness[i]
        }

    d.closeNetwork()

    return pipes


if __name__ == "__main__":

    input_file = "../networks/test_network.inp"

    pipes = read_network(input_file)

    print("\n")
    print("=" * 80)
    print("EPANET NETWORK READER")
    print("=" * 80)

    print("\n--- PIPES ---")

    for pipe_id, data in pipes.items():

        print(
            f"{pipe_id}: "
            f"{data['start_node']} -> "
            f"{data['end_node']} | "
            f"Length: {data['length']:.2f} m | "
            f"Diameter: DN{data['diameter']:.0f} | "
            f"Roughness: {data['roughness']:.2f}"
        )