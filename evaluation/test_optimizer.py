from evaluation.network_optimizer_optuna import (
    optimize_network,
    get_closest_infeasible_solution,
    generate_closest_infeasible_solution
)

from evaluation.optimization_config import criteria

input_file = "networks/test.inp"

study = optimize_network(
    input_file,
    criteria,
    n_trials=20
)

closest = get_closest_infeasible_solution(
    study
)

closest_file = (
    generate_closest_infeasible_solution(
        study,
        input_file,
        "networks/optimized"
    )
)

if closest is None:

    print("Няма недопустими решения.")

else:

    print("\n")
    print("=" * 70)
    print("CLOSEST INFEASIBLE SOLUTION")
    print("=" * 70)

    print(
        f"Trial: {closest.number}"
    )

    print(
        f"Violation: "
        f"{closest.user_attrs['constraint_violation']:.4f}"
    )

    print(
        f"Min pressure: "
        f"{closest.user_attrs['min_pressure']:.3f} m"
    )

    print(
        f"Max pressure: "
        f"{closest.user_attrs['max_pressure']:.3f} m"
    )

    print(
        f"Max velocity: "
        f"{closest.user_attrs['max_velocity']:.3f} m/s"
    )

    print("\nViolations:")

    for name, value in (
            closest.user_attrs["violations"].items()
    ):
        print(
            f"{name}: {value:.4f}"
        )

    print("\nDiameters:")

    for pipe_id, diameter in (
            closest.params.items()
    ):
        print(
            f"{pipe_id}: DN{diameter}"
        )

print("\nClosest infeasible solution file:")

if closest_file:
    print(closest_file)
else:
    print("No infeasible solution found.")
