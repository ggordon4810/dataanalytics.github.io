import os

import pandas as pd

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from graphing import (
    build_figure_settings,
    create_graph,
    save_figure,
    validate_output_format,
)

from helpers import (
    generate_safe_filename,
    read_csv_file,
    validate_columns,
    validate_uploaded_file,
)


app = Flask(__name__)

# Development secret key.
# For deployment, replace this with an environment variable.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "figureforge-development-secret-key"
)


# --------------------------------------------------
# Folder configuration
# --------------------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
GENERATED_FOLDER = os.path.join(BASE_DIR, "generated")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["GENERATED_FOLDER"] = GENERATED_FOLDER


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# CSV Upload
# --------------------------------------------------

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        try:
            uploaded_file = request.files.get("file")

            # Validate the uploaded file.
            validate_uploaded_file(uploaded_file)

            # Generate a safe unique filename.
            safe_filename = generate_safe_filename(
                uploaded_file.filename
            )

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                safe_filename
            )

            # Save the uploaded CSV.
            uploaded_file.save(filepath)

            # Make sure the saved CSV contains usable data.
            read_csv_file(filepath)

            # Store the current dataset filename.
            session["data_filename"] = safe_filename

            return redirect(url_for("configure"))

        except ValueError as error:
            return render_template(
                "upload.html",
                error=str(error)
            )

    return render_template("upload.html")


# --------------------------------------------------
# Manual Data Entry
# --------------------------------------------------

@app.route("/manual", methods=["GET", "POST"])
def manual_entry():
    if request.method == "POST":
        try:
            x_values = request.form.getlist("x_value")
            y_values = request.form.getlist("y_value")
            error_values = request.form.getlist("error_value")

            if len(x_values) < 2 or len(y_values) < 2:
                raise ValueError(
                    "At least two measurements are required."
                )

            if len(x_values) != len(y_values):
                raise ValueError(
                    "Each X value must have a corresponding Y value."
                )

            rows = []

            for index in range(len(x_values)):
                x_value = str(x_values[index]).strip()
                y_value = str(y_values[index]).strip()

                if not x_value:
                    raise ValueError(
                        f"X value {index + 1} is required."
                    )

                if not y_value:
                    raise ValueError(
                        f"Y value {index + 1} is required."
                    )

                try:
                    y_number = float(y_value)
                except ValueError:
                    raise ValueError(
                        f"Y value {index + 1} must be numeric."
                    )

                error_number = None

                if index < len(error_values):
                    error_value = str(
                        error_values[index]
                    ).strip()

                    if error_value:
                        try:
                            error_number = float(error_value)
                        except ValueError:
                            raise ValueError(
                                f"Error value {index + 1} "
                                "must be numeric."
                            )

                        if error_number < 0:
                            raise ValueError(
                                "Error-bar values cannot be negative."
                            )

                rows.append(
                    {
                        "X": x_value,
                        "Y": y_number,
                        "Error": error_number,
                    }
                )

            dataframe = pd.DataFrame(rows)

            # Convert X to numeric when every X value is numeric.
            numeric_x = pd.to_numeric(
                dataframe["X"],
                errors="coerce"
            )

            if numeric_x.notna().all():
                dataframe["X"] = numeric_x

            safe_filename = generate_safe_filename(
                "manual_data.csv"
            )

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                safe_filename
            )

            dataframe.to_csv(
                filepath,
                index=False
            )

            session["data_filename"] = safe_filename

            return redirect(url_for("configure"))

        except ValueError as error:
            return render_template(
                "manual_entry.html",
                error=str(error)
            )

    return render_template("manual_entry.html")


# --------------------------------------------------
# Configure Figure
# --------------------------------------------------

@app.route("/configure", methods=["GET", "POST"])
def configure():
    data_filename = session.get("data_filename")

    if not data_filename:
        flash(
            "Please upload or enter data before configuring a figure.",
            "error"
        )
        return redirect(url_for("upload"))

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        data_filename
    )

    try:
        dataframe = read_csv_file(filepath)

    except ValueError as error:
        return render_template(
            "error.html",
            message=str(error)
        ), 400

    columns = list(dataframe.columns)

    preview_rows = dataframe.head(5).to_dict(
        orient="records"
    )

    if request.method == "POST":
        try:
            graph_type = request.form.get("graph_type")
            x_column = request.form.get("x_column")
            y_column = request.form.get("y_column")

            error_column = request.form.get("error_column")

            if error_column is not None:
                error_column = error_column.strip()

                if not error_column:
                    error_column = None

            # Clean and validate selected plotting data.
            cleaned_dataframe = validate_columns(
                dataframe,
                x_column,
                y_column,
                error_column
            )

            title = request.form.get("title")
            x_label = request.form.get("x_label")
            y_label = request.form.get("y_label")

            width = request.form.get("width", 8)
            height = request.form.get("height", 6)
            dpi = request.form.get("dpi", 300)

            marker_size = request.form.get(
                "marker_size",
                40
            )

            line_width = request.form.get(
                "line_width",
                2
            )

            show_grid = (
                request.form.get("show_grid")
                is not None
            )

            output_format = validate_output_format(
                request.form.get(
                    "output_format",
                    "png"
                )
            )

            settings = build_figure_settings(
                title=title,
                x_label=x_label,
                y_label=y_label,
                width=width,
                height=height,
                dpi=dpi,
                marker_size=marker_size,
                line_width=line_width,
                show_grid=show_grid,
            )

            fig, ax = create_graph(
                graph_type,
                cleaned_dataframe,
                x_column,
                y_column,
                settings,
                error_column
            )

            saved_path = save_figure(
                fig=fig,
                output_directory=app.config[
                    "GENERATED_FOLDER"
                ],
                filename="figure",
                output_format=output_format,
                dpi=settings["dpi"],
            )

            generated_filename = os.path.basename(
                saved_path
            )

            session["generated_filename"] = (
                generated_filename
            )

            session["graph_type"] = graph_type
            session["x_column"] = x_column
            session["y_column"] = y_column
            session["output_format"] = output_format
            session["dpi"] = settings["dpi"]

            return redirect(url_for("preview"))

        except ValueError as error:
            return render_template(
                "configure.html",
                error=str(error),
                columns=columns,
                preview_rows=preview_rows,
            )

    return render_template(
        "configure.html",
        columns=columns,
        preview_rows=preview_rows,
    )


# --------------------------------------------------
# Preview
# --------------------------------------------------

@app.route("/preview")
def preview():
    generated_filename = session.get(
        "generated_filename"
    )

    if not generated_filename:
        flash(
            "No generated figure is available.",
            "error"
        )
        return redirect(url_for("upload"))

    generated_path = os.path.join(
        app.config["GENERATED_FOLDER"],
        generated_filename
    )

    if not os.path.exists(generated_path):
        return render_template(
            "error.html",
            message="The generated figure could not be found."
        ), 404

    graph_type = session.get("graph_type")
    x_column = session.get("x_column")
    y_column = session.get("y_column")
    output_format = session.get("output_format")
    dpi = session.get("dpi")

    preview_url = None

    if output_format in {"png", "svg"}:
        preview_url = url_for(
            "generated_file",
            filename=generated_filename
        )

    data_preview = None

    data_filename = session.get("data_filename")

    if data_filename:
        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            data_filename
        )

        try:
            dataframe = read_csv_file(filepath)

            data_preview = dataframe.head(
                10
            ).to_dict(
                orient="records"
            )

        except ValueError:
            data_preview = None

    return render_template(
        "preview.html",
        filename=generated_filename,
        preview_url=preview_url,
        graph_type=graph_type,
        x_column=x_column,
        y_column=y_column,
        output_format=output_format,
        dpi=dpi,
        data_preview=data_preview,
    )


# --------------------------------------------------
# Display Generated File
# --------------------------------------------------

@app.route("/generated/<path:filename>")
def generated_file(filename):
    return send_from_directory(
        app.config["GENERATED_FOLDER"],
        filename
    )


# --------------------------------------------------
# Download Figure
# --------------------------------------------------

@app.route("/download/<path:filename>")
def download(filename):
    filepath = os.path.join(
        app.config["GENERATED_FOLDER"],
        filename
    )

    if not os.path.exists(filepath):
        return render_template(
            "error.html",
            message="The requested figure could not be found."
        ), 404

    return send_from_directory(
        app.config["GENERATED_FOLDER"],
        filename,
        as_attachment=True
    )


# --------------------------------------------------
# Error Handlers
# --------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "error.html",
        message="The requested page could not be found."
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        "error.html",
        message="An unexpected server error occurred."
    ), 500


# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
