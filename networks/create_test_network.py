from epyt import epanet


def create_network():
    d = epanet()

    d.createProject()

    d.initializeEPANET(
        d.ToolkitConstants.EN_LPS,
        d.ToolkitConstants.EN_HW
    )

    # -------------------------------------------------
    # РЕЗЕРВОАР
    # -------------------------------------------------

    res_index = d.addNodeReservoir("R1", [0, 0])

    # Постоянен напор на резервоара = 100 m
    pattern_index = d.addPattern("RES_HEAD")

    d.setNodeReservoirHeadPatternIndex(
        res_index,
        pattern_index
    )

    d.setPattern(
        pattern_index,
        [1.0]
    )

    # -------------------------------------------------
    # ВЪЗЛИ
    # -------------------------------------------------

    d.addNodeJunction("J1", [100, 0], 95, 5)
    d.addNodeJunction("J2", [200, 100], 90, 3)
    d.addNodeJunction("J3", [300, 0], 88, 4)
    d.addNodeJunction("J4", [100, -100], 85, 4)
    d.addNodeJunction("J5", [100, -200], 82, 3)

    # -------------------------------------------------
    # ТРЪБИ
    # -------------------------------------------------

    d.addLinkPipe("P1", "R1", "J1", 300, 160, 100)
    d.addLinkPipe("P2", "J1", "J2", 200, 110, 100)
    d.addLinkPipe("P3", "J1", "J3", 250, 110, 100)
    d.addLinkPipe("P4", "J1", "J4", 200, 90, 100)
    d.addLinkPipe("P5", "J4", "J5", 150, 90, 100)
    d.addLinkPipe("P6", "J2", "J3", 180, 90, 100)

    # -------------------------------------------------
    # ЗАПИС НА .INP
    # -------------------------------------------------

    result = d.saveInputFile("test_network.inp")

    print("saveInputFile() returned:", result)

    d.closeNetwork()


if __name__ == "__main__":
    create_network()