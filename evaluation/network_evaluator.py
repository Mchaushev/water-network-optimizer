from epyt import epanet
import numpy as np


def evaluate_network(inp_file, criteria):

    d = epanet(inp_file)
    d.solveCompleteHydraulics()

    # =========================
    # NODE RESULTS
    # =========================

    node_names = d.getNodeNameID()
    pressures = d.getNodePressure()

    # Получаваме само junction възлите
    junction_names = d.getNodeJunctionNameID()

    junction_indices = [
        node_names.index(name)
        for name in junction_names
    ]

    junction_pressures = pressures[junction_indices]

    # Минимално налягане
    min_pressure = np.min(junction_pressures)
    min_pressure_local_index = np.argmin(junction_pressures)
    min_pressure_node = junction_names[min_pressure_local_index]

    # Максимално налягане
    max_pressure = np.max(junction_pressures)
    max_pressure_local_index = np.argmax(junction_pressures)
    max_pressure_node = junction_names[max_pressure_local_index]

    # =========================
    # PIPE RESULTS
    # =========================

    pipe_names = d.getLinkNameID()
    velocities = d.getLinkVelocity()

    # Максимална скорост
    max_velocity = np.max(velocities)
    max_velocity_index = np.argmax(velocities)
    max_velocity_pipe = pipe_names[max_velocity_index]

    # =========================
    # CRITERIA
    # =========================

    min_pressure_required = criteria["min_pressure"]
    max_pressure_allowed = criteria["max_pressure"]
    max_velocity_allowed = criteria["max_velocity"]

    # =========================
    # ENGINEERING CHECK
    # =========================

    pressure_min_ok = min_pressure >= min_pressure_required
    pressure_max_ok = max_pressure <= max_pressure_allowed
    velocity_ok = max_velocity <= max_velocity_allowed

    feasible = (
        pressure_min_ok
        and pressure_max_ok
        and velocity_ok
    )

    # =========================
    # RESULT
    # =========================

    result = {
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

    return result


# =========================
# TEST
# =========================

if __name__ == "__main__":

    criteria = {
        "min_pressure": 20.0,
        "max_pressure": 60.0,
        "max_velocity": 2.0
    }

    result = evaluate_network(
        "../networks/test_network.inp",
        criteria
    )

    print("\n=== HYDRAULIC CHECK ===")

    print(
        f"Minimum pressure: "
        f"{result['min_pressure']:.2f} m "
        f"({result['min_pressure_node']})"
    )

    print(
        f"Maximum pressure: "
        f"{result['max_pressure']:.2f} m "
        f"({result['max_pressure_node']})"
    )

    print(
        f"Maximum velocity: "
        f"{result['max_velocity']:.2f} m/s "
        f"({result['max_velocity_pipe']})"
    )

    print("\n=== REQUIREMENTS ===")

    print(
        f"Pressure >= {criteria['min_pressure']:.2f} m: "
        f"{'OK' if result['pressure_min_ok'] else 'NOT OK'}"
    )

    print(
        f"Pressure <= {criteria['max_pressure']:.2f} m: "
        f"{'OK' if result['pressure_max_ok'] else 'NOT OK'}"
    )

    print(
        f"Velocity <= {criteria['max_velocity']:.2f} m/s: "
        f"{'OK' if result['velocity_ok'] else 'NOT OK'}"
    )

    print(
        "\nSTATUS: "
        f"{'FEASIBLE' if result['feasible'] else 'NOT FEASIBLE'}"
    )