from epyt import epanet


def change_pipe_diameter(inp_file, output_file, pipe_id, diameter):
    """
    Changes the diameter of a pipe in an EPANET network
    and saves the modified network as a new .inp file.
    """

    d = epanet(inp_file)

    pipe_index = d.getLinkIndex(pipe_id)

    d.setLinkDiameter(pipe_index, diameter)

    d.saveInputFile(output_file)

    d.closeNetwork()


def set_pipe_diameters(inp_file, pipe_diameters):
    """
    Loads an EPANET network and changes the diameters
    of multiple pipes.

    Parameters:
        inp_file:
            Path to the original .inp file.

        pipe_diameters:
            Dictionary with pipe IDs and diameters.

    Returns:
        EPANET network object with modified diameters.
    """

    d = epanet(inp_file)

    pipe_ids = list(pipe_diameters.keys())
    diameters = list(pipe_diameters.values())

    pipe_indices = d.getLinkIndex(pipe_ids)

    d.setLinkDiameter(
        pipe_indices,
        diameters
    )

    return d


def save_pipe_configuration(
        inp_file,
        output_file,
        pipe_diameters
):
    """
    Loads an EPANET network, changes the diameters
    of multiple pipes and saves the result as a new .inp file.

    Parameters:
        inp_file:
            Path to the original EPANET .inp file.

        output_file:
            Path for the new .inp file.

        pipe_diameters:
            Dictionary with pipe IDs and diameters.
    """

    d = set_pipe_diameters(
        inp_file,
        pipe_diameters
    )

    d.saveInputFile(output_file)

    d.closeNetwork()
