import os

import matplotlib.pyplot as plt
import numpy as np

from calculations import calculate_linear_regression

SUPPORTED_GRAPH_TYPES = {"scatter", "line", "bar"}
SUPPORTED_OUTPUT_FORMATS = {"png", "svg", "pdf"}

def validate_graph_type(graph_type):
  if graph_type is None:
    raise ValueError ("Graph type is required.")

  graph_type = str(graph_type).strip().lower()

  if graph_type not in SUPPORTED_GRAPH_TYPES:
    raise ValueError ("Supported graph types are: scatter, line, and bar.")

  return graph_type
    
def validate_output_format(output_format):
    if output_format is None:
      output_format = "png"
    # Convert output_format into a string.
    output_format = str(output_format).strip().lower()

    if output_format not in SUPPORTED_OUTPUT_FORMATS:
      raise ValueError ("Supported output formats are: png, svg, pdf.")

    return output_format

def build_figure_settings(
    title=None,
    x_label=None,
    y_label=None,
    width=8,
    height=6,
    dpi=300,
    marker_size=40,
    line_width=2,
    show_grid=True
):
    if title is None:
      title = ""
    else:
      title = str(title).strip()
      
    if x_label is None:
      x_label = ""
    else:
      x_label = str(x_label).strip()

    if y_label is None:
      y_label = ""
    else:
      y_label = str(y_label).strip()

    width = parse_optional_float(width, "Width")
    height = parse_optional_float(height, "Height")
    marker_size = parse_optional_float(marker_size, "Marker Size")
    line_width = parse_optional_float(line_width, "Line Width")
    dpi = parse_positive_integer(dpi, "DPI", default=300)

    show_grid = bool(show_grid)

    settings = {
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "width": width,
        "height": height,
        "dpi": dpi,
        "marker_size": marker_size,
        "line_width": line_width,
        "show_grid": show_grid,
    }

    return settings

def apply_common_styling(ax, settings):
    # Check that the axes exist.
    if ax is None:
        raise ValueError("Plot axes are missing.")

    # Check that graph settings exist.
    if settings is None:
        raise ValueError("Graph settings are missing.")

    # Apply the graph title and labels.
    ax.set_title(settings["title"])
    ax.set_xlabel(settings["x_label"])
    ax.set_ylabel(settings["y_label"])

    # Turn the grid on or off.
    ax.grid(
        settings["show_grid"],
        linestyle="--",
        alpha=0.5
    )

    # Make the axis labels easier to read.
    ax.tick_params(labelsize=11)

    # Remove unnecessary borders.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Prevent labels from being cut off.
    ax.figure.tight_layout()

    return ax

def create_scatter_plot(
    dataframe,
    x_column,
    y_column,
    settings,
    error_column=None
):
    """
    Create a scatter plot from selected DataFrame columns.

    Args:
        dataframe: Cleaned pandas DataFrame.
        x_column: Name of the X-axis column.
        y_column: Name of the Y-axis column.
        settings: Dictionary of figure settings.
        error_column: Optional column containing Y-error values.

    Returns:
        A tuple containing the Matplotlib figure and axes.

    Raises:
        ValueError: If the data or selected columns are invalid.
    """

    # Check that the dataset contains data.
    if dataframe is None or dataframe.empty:
        raise ValueError("The dataset is empty.")

    # Check that the selected columns exist.
    if x_column not in dataframe.columns:
        raise ValueError("The selected X column was not found.")

    if y_column not in dataframe.columns:
        raise ValueError("The selected Y column was not found.")

    if error_column is not None:
        if error_column not in dataframe.columns:
            raise ValueError("The selected error column was not found.")

    # Create a new figure and axes.
    fig, ax = plt.subplots(
        figsize=(
            settings["width"],
            settings["height"]
        ),
        dpi=settings["dpi"]
    )

    # Get the X and Y values.
    x_values = dataframe[x_column]
    y_values = dataframe[y_column]

    # Draw error bars when an error column was selected.
    if error_column is not None:
        error_values = dataframe[error_column]

        ax.errorbar(
            x_values,
            y_values,
            yerr=error_values,
            fmt="o",
            linestyle="none",
            markersize=settings["marker_size"] ** 0.5,
            capsize=4
        )

    # Otherwise, create a standard scatter plot.
    else:
        ax.scatter(
            x_values,
            y_values,
            s=settings["marker_size"]
        )

    # Apply titles, labels, grid, and layout.
    apply_common_styling(ax, settings)

    return fig, ax

def create_line_plot(
    dataframe,
    x_column,
    y_column,
    settings,
    error_column=None
):
    # Validate the data.
    if dataframe is None or dataframe.empty:
        raise ValueError("The dataset is empty.")

    if x_column not in dataframe.columns:
        raise ValueError("The selected X column was not found.")

    if y_column not in dataframe.columns:
        raise ValueError("The selected Y column was not found.")

    if error_column is not None and error_column not in dataframe.columns:
        raise ValueError("The selected error column was not found.")

    # Sort numeric X values.
    if pd.api.types.is_numeric_dtype(dataframe[x_column]):
        dataframe = dataframe.sort_values(by=x_column)

    # Create the figure.
    fig, ax = plt.subplots(
        figsize=(settings["width"], settings["height"]),
        dpi=settings["dpi"]
    )

    x_values = dataframe[x_column]
    y_values = dataframe[y_column]

    if error_column is not None:
        error_values = dataframe[error_column]

        ax.errorbar(
            x_values,
            y_values,
            yerr=error_values,
            fmt="o-",
            linewidth=settings["line_width"],
            markersize=settings["marker_size"] ** 0.5,
            capsize=4
        )

    else:
        ax.plot(
            x_values,
            y_values,
            marker="o",
            linewidth=settings["line_width"],
            markersize=settings["marker_size"] ** 0.5
        )

    apply_common_styling(ax, settings)

    return fig, ax


def create_bar_plot(
    dataframe,
    x_column,
    y_column,
    settings,
    error_column=None
):
    # Validate the data.
    if dataframe is None or dataframe.empty:
        raise ValueError("The dataset is empty.")

    if x_column not in dataframe.columns:
        raise ValueError("The selected X column was not found.")

    if y_column not in dataframe.columns:
        raise ValueError("The selected Y column was not found.")

    if error_column is not None and error_column not in dataframe.columns:
        raise ValueError("The selected error column was not found.")

    # Create the figure.
    fig, ax = plt.subplots(
        figsize=(settings["width"], settings["height"]),
        dpi=settings["dpi"]
    )

    x_values = dataframe[x_column]
    y_values = dataframe[y_column]

    if error_column is not None:
        error_values = dataframe[error_column]

        ax.bar(
            x_values,
            y_values,
            yerr=error_values,
            capsize=4
        )

    else:
        ax.bar(
            x_values,
            y_values
        )

    # Rotate labels if there are many categories.
    if len(x_values) > 6:
        ax.tick_params(axis="x", labelrotation=45)

    apply_common_styling(ax, settings)

    return fig, ax
  
def save_figure(
    fig,
    output_directory,
    filename,
    output_format="png",
    dpi=300
):
    # Check that a figure exists.
    if fig is None:
        raise ValueError("There is no figure to save.")

    # Validate the output format.
    output_format = validate_output_format(output_format)

    # Create the output directory if necessary.
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Remove any existing extension.
    filename = os.path.splitext(filename)[0]

    # Generate a safe filename.
    filename = generate_safe_filename(f"{filename}.{output_format}")

    # Build the complete path.
    save_path = os.path.join(
        output_directory,
        filename
    )

    # Save the figure.
    fig.savefig(
        save_path,
        format=output_format,
        dpi=dpi,
        bbox_inches="tight"
    )

    # Close the figure.
    plt.close(fig)

    return save_path

 def create_graph(
    graph_type,
    dataframe,
    x_column,
    y_column,
    settings,
    error_column=None
):
    """
    Create the requested graph type.

    Args:
        graph_type: Type of graph to create.
        dataframe: Data to plot.
        x_column: X-axis column.
        y_column: Y-axis column.
        settings: Figure settings.
        error_column: Optional error-bar column.

    Returns:
        A Matplotlib figure and axes.
    """

    # Validate the graph type.
    graph_type = validate_graph_type(graph_type)

    if graph_type == "scatter":
        fig, ax = create_scatter_plot(
            dataframe,
            x_column,
            y_column,
            settings,
            error_column
        )

    elif graph_type == "line":
        fig, ax = create_line_plot(
            dataframe,
            x_column,
            y_column,
            settings,
            error_column
        )

    elif graph_type == "bar":
        fig, ax = create_bar_plot(
            dataframe,
            x_column,
            y_column,
            settings,
            error_column
        )

    return fig, ax
