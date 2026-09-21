from epyt import epanet


def run_simulation(inp_file):
    d = epanet(inp_file)

    print("\n=== WATER NETWORK HYDRAULIC SIMULATION ===")

    d.solveCompleteHydraulics()

    # =========================
    # NODE RESULTS
    # =========================

    node_names = d.getNodeNameID()
    pressures = d.getNodePressure()
    demands = d.getNodeActualDemand()
    heads = d.getNodeHydraulicHead()

    print("\n--- NODE RESULTS ---")

    for i, name in enumerate(node_names):
        print(
            f"{name:>3} | "
            f"Demand: {demands[i]:8.3f} L/s | "
            f"Pressure: {pressures[i]:8.3f} m | "
            f"Head: {heads[i]:8.3f} m"
        )

    # =========================
    # PIPE RESULTS
    # =========================

    pipe_names = d.getLinkNameID()
    flows = d.getLinkFlows()
    velocities = d.getLinkVelocity()
    headloss = d.getLinkHeadloss()

    print("\n--- PIPE RESULTS ---")

    for i, name in enumerate(pipe_names):
        print(
            f"{name:>3} | "
            f"Flow: {flows[i]:8.3f} L/s | "
            f"Velocity: {velocities[i]:8.3f} m/s | "
            f"Headloss: {headloss[i]:8.3f} m"
        )

    d.closeNetwork()


if __name__ == "__main__":
    input_file = "../networks/test_network_P4_160.inp"

    run_simulation(input_file)
