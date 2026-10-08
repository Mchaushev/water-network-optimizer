from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    send_file
)

from evaluation.network_optimizer_optuna import (
    optimize_network,
    generate_top_solutions,
    get_closest_infeasible_solution,
    generate_closest_infeasible_solution,
    get_top_solutions
)

from evaluation.network_reader import read_network

from evaluation.optimization_config import (
    criteria,
    output_directory
)

import os

app = Flask(__name__)

app.secret_key = "water-network-optimizer"


@app.route("/")
def home():

    input_file = session.get(
        "network_file"
    )

    if input_file and os.path.exists(input_file):

        pipes = read_network(input_file)
        network_name = os.path.basename(input_file)

    else:

        pipes = {}
        network_name = None

    return render_template(
        "index.html",
        network_name=network_name,
        pipes=pipes,
        criteria=criteria
    )


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["network_file"]

    if file.filename == "":
        return "No file selected"

    upload_directory = "networks/uploads"

    os.makedirs(
        upload_directory,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_directory,
        file.filename
    )

    file.save(file_path)

    session["network_file"] = file_path

    return redirect("/")


@app.route("/optimize", methods=["POST"])
def optimize():
    session.pop("csv_file", None)

    min_pressure = float(
        request.form["min_pressure"]
    )

    max_pressure = float(
        request.form["max_pressure"]
    )

    max_velocity = float(
        request.form["max_velocity"]
    )

    trials = int(
        request.form["trials"]
    )

    criteria = {
        "min_pressure": min_pressure,
        "max_pressure": max_pressure,
        "max_velocity": max_velocity
    }

    input_file = session.get(
        "network_file"
    )

    if not input_file or not os.path.exists(input_file):
        return redirect("/")

    # Run Optuna optimization
    study = optimize_network(
        input_file,
        criteria,
        n_trials=trials
    )

    # Get Top 3 feasible solutions
    top_solutions = get_top_solutions(
        study,
        max_solutions=3
    )

    # ---------------------------------------------------------
    # CASE 1: At least one feasible solution exists
    # ---------------------------------------------------------

    if top_solutions:
        results, csv_file = generate_top_solutions(
            study,
            input_file,
            criteria,
            output_directory
        )
        session["csv_file"] = csv_file

        best_result = results[0]


        return render_template(
            "results.html",
            trials=trials,
            best_result=best_result,
            results=results,
            csv_file=csv_file,
            feasible=True
        )

    # ---------------------------------------------------------
    # CASE 2: No feasible solution exists
    # ---------------------------------------------------------

    closest_trial = get_closest_infeasible_solution(
        study
    )

    closest_file = generate_closest_infeasible_solution(
        study,
        input_file,
        output_directory
    )

    session["closest_infeasible_file"] = closest_file

    closest_report = None

    if closest_trial:
        min_pressure = closest_trial.user_attrs["min_pressure"]
        max_pressure = closest_trial.user_attrs["max_pressure"]
        max_velocity = closest_trial.user_attrs["max_velocity"]

        pressure_min_ok = (
                min_pressure >= criteria["min_pressure"]
        )

        pressure_max_ok = (
                max_pressure <= criteria["max_pressure"]
        )

        velocity_ok = (
                max_velocity <= criteria["max_velocity"]
        )

        closest_report = {
            "trial": closest_trial.number,
            "constraint_violation":
                closest_trial.user_attrs["constraint_violation"],

            "min_pressure": min_pressure,
            "max_pressure": max_pressure,
            "max_velocity": max_velocity,

            "pressure_min_ok": pressure_min_ok,
            "pressure_max_ok": pressure_max_ok,
            "velocity_ok": velocity_ok
        }

    return render_template(
        "results.html",
        trials=trials,
        best_result=None,
        results=[],
        csv_file=None,
        feasible=False,
        closest_trial=closest_trial,
        closest_file=closest_file,
        closest_report=closest_report,
        criteria=criteria
    )
@app.route("/download-csv")
def download_csv():

    csv_file = session.get("csv_file")

    if not csv_file:
        return "CSV file not found", 404

    if not os.path.exists(csv_file):
        return "CSV file not found", 404

    return send_file(
        csv_file,
        as_attachment=True,
        download_name="optuna_top_3_solutions.csv"
    )

@app.route("/download-solution/<int:rank>")
def download_solution(rank):

    if rank not in [1, 2, 3]:
        return "Solution not found", 404

    solution_file = os.path.join(
        output_directory,
        f"optuna_solution_{rank}.inp"
    )

    if not os.path.exists(solution_file):
        return "Solution file not found", 404

    return send_file(
        solution_file,
        as_attachment=True,
        download_name=f"optuna_solution_{rank}.inp"
    )


@app.route("/download-closest-infeasible")
def download_closest_infeasible():

    inp_file = session.get("closest_infeasible_file")

    if not inp_file:
        return "INP file not found", 404

    if not os.path.exists(inp_file):
        return "INP file not found", 404

    return send_file(
        inp_file,
        as_attachment=True,
        download_name="closest_infeasible_solution.inp"
    )

if __name__ == "__main__":
    app.run(debug=True)
