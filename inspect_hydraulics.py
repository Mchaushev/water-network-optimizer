from epyt import epanet
import inspect

d = epanet("test_network.inp")

print("=== Hydraulic Analysis ===")

methods = [
    "openHydraulicAnalysis",
    "initializeHydraulicAnalysis",
    "runHydraulicAnalysis",
    "nextHydraulicAnalysisStep",
    "closeHydraulicAnalysis",
    "solveCompleteHydraulics",
    "getNodePressure",
    "getLinkVelocity",
    "getLinkFlows",
    "getLinkHeadloss",
]

for name in methods:
    print(f"\n--- {name} ---")

    if hasattr(d, name):
        method = getattr(d, name)
        print(inspect.signature(method))
        print(method.__doc__)
    else:
        print("NOT FOUND")

d.closeNetwork()