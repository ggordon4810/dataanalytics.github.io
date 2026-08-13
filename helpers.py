import os
import uuid

import pandas as pd

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    if not isinstance(filename, str):
        return False

    if "." not in filename:
        return False

    name, extension = filename.rsplit(".", 1)

    extension = extension.lower()

    return extension in ALLOWED_EXTENSIONS

def generate_safe_filename(filename):
    # Check that a filename was provided.
    if filename is None:
        raise ValueError("The filename is invalid.")

    # Remove unsafe characters.
    filename = secure_filename(filename)

    # Make sure the cleaned filename is not empty.
    if not filename:
        raise ValueError("The filename is invalid.")

    # Split into the base filename and extension.
    name, extension = filename.rsplit(".", 1)

    # Generate a unique identifier.
    unique_id = str(uuid.uuid4())[:8]

    # Build the new filename.
    new_filename = f"{name}_{unique_id}.{extension}"

    return new_filename


def validate_uploaded_file(file):
    if file is None:
        raise ValueError("No file was uploaded.")

    if not file.filename:
        raise ValueError("Please select a CSV file.")

    filename = file.filename.strip()

    if not filename:
        raise ValueError("Please select a CSV file.")

    if not allowed_file(filename):
        raise ValueError("Only CSV files are supported.")

    return True

def read_csv_file(filepath):

  if not os.path.exists (filepath):
    raise ValueError ("uploaded file could not be found")

  try:
    df = pd.read_csv(filepath)
  except pd.errors.EmptyDataError:
    raise ValueError("The uploaded CSV file is empty")
  except pd.errors.ParserError:
    raise ValueError ("The uploaded CSV file could not be read")
  except Exception as e:
    raise ValueError(f"An unexpected error occurred: {e}")

  if df.empty:
    raise ValueError ("The CSV contains no data.")

  if len(df.columns) < 2:
    raise ValueError("The CSV must contain at least two columns.")

  df.columns = df.columns.str.strip()

  if (df.columns == "").any():
    raise ValueError("Every column must have a name.")


  if any(df.columns.duplicated()):
    raise ValueError ("Every column must have a unique name")
  return df

def validate_columns(
    dataframe,
    x_column,
    y_column,
    error_column=None
):
    """
    Validate selected columns and return a cleaned copy
    of the data.

    Args:
        dataframe: pandas DataFrame containing the data.
        x_column: Name of the selected X-axis column.
        y_column: Name of the selected Y-axis column.
        error_column: Optional error-bar column.

    Returns:
        A cleaned pandas DataFrame containing only the
        selected columns.

    Raises:
        ValueError: If the selected columns or data are invalid.
    """

    # Check that a dataset is available.
    if dataframe is None or dataframe.empty:
        raise ValueError("The dataset is not available.")

    # Check that X and Y columns were selected.
    if x_column is None or not str(x_column).strip():
        raise ValueError("An X-axis column is required.")

    if y_column is None or not str(y_column).strip():
        raise ValueError("A Y-axis column is required.")

    # Clean the selected column names.
    x_column = str(x_column).strip()
    y_column = str(y_column).strip()

    if error_column is not None:
        error_column = str(error_column).strip()

        if not error_column:
            error_column = None

    # Check that selected columns exist.
    if x_column not in dataframe.columns:
        raise ValueError(
            f"The selected X-axis column '{x_column}' was not found."
        )

    if y_column not in dataframe.columns:
        raise ValueError(
            f"The selected Y-axis column '{y_column}' was not found."
        )

    if (
        error_column is not None
        and error_column not in dataframe.columns
    ):
        raise ValueError(
            f"The selected error-bar column '{error_column}' was not found."
        )

    # X and Y cannot be the same column.
    if x_column == y_column:
        raise ValueError(
            "X and Y must use different columns."
        )

    # Error column must be different from X and Y.
    if error_column is not None:
        if error_column == x_column or error_column == y_column:
            raise ValueError(
                "The error-bar column must be different "
                "from the X and Y columns."
            )

    # Build a list of selected columns.
    selected_columns = [
        x_column,
        y_column
    ]

    if error_column is not None:
        selected_columns.append(error_column)

    # Create a copy of only the selected data.
    df_copy = dataframe[selected_columns].copy()

    # Convert the Y column to numeric.
    df_copy[y_column] = pd.to_numeric(
        df_copy[y_column],
        errors="coerce"
    )

    # Convert the error column to numeric if present.
    if error_column is not None:
        df_copy[error_column] = pd.to_numeric(
            df_copy[error_column],
            errors="coerce"
        )

    # Attempt to convert X values to numeric.
    numeric_x = pd.to_numeric(
        df_copy[x_column],
        errors="coerce"
    )

    # If every nonmissing X value converted successfully,
    # use the numeric version.
    original_nonmissing = df_copy[x_column].notna().sum()
    numeric_nonmissing = numeric_x.notna().sum()

    if numeric_nonmissing == original_nonmissing:
        df_copy[x_column] = numeric_x

    # Determine which columns are required.
    required_columns = [
        x_column,
        y_column
    ]

    if error_column is not None:
        required_columns.append(error_column)

    # Remove rows containing missing required values.
    df_copy = df_copy.dropna(
        subset=required_columns
    )

    # Require at least two valid rows.
    if len(df_copy) < 2:
        raise ValueError(
            "At least two valid measurements are required."
        )

    # Error-bar values cannot be negative.
    if error_column is not None:
        if (df_copy[error_column] < 0).any():
            raise ValueError(
                "Error-bar values cannot be negative."
            )

    return df_copy

def parse_optional_float(value, field_name):
    """
    Convert an optional form value into a float.

    Args:
        value: Value entered by the user.
        field_name: Name used in the error message.

    Returns:
        A float when a value is provided, otherwise None.

    Raises:
        ValueError: If the value cannot be converted to a float.
    """

    if value is None:
        return None

    # Convert the value to a string and remove whitespace.
    value = str(value).strip()

    # An empty optional field becomes None.
    if not value:
        return None

    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be a valid number."
        ) from exc


def parse_positive_integer(value, field_name, default=None):
    """
    Convert an optional form value into a positive integer.

    Args:
        value: Value entered by the user.
        field_name: Name used in the error message.
        default: Value returned when the field is empty.

    Returns:
        A positive integer or the supplied default value.

    Raises:
        ValueError: If the value is not a positive whole number.
    """

    if value is None:
        return default

    # Convert the value to a string and remove whitespace.
    value = str(value).strip()

    if not value:
        return default

    try:
        integer_value = int(value)
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be a whole number."
        ) from exc

    if integer_value <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return integer_value

