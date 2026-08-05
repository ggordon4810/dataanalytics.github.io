import os
import uuid

import pandas as pd

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"csv"} 


def allowed_file(filename):
    """
    Check whether a filename has an allowed file extension.

    Args:
        filename (str): Name of the uploaded file.

    Returns:
        bool: True if the file extension is allowed, otherwise False.
    """

    # Check that the filename is a string.
    if not isinstance(filename, str):
        return False

    # Check that the filename contains a file extension.
    if "." not in filename:
        return False

    # Split the filename into the name and extension.
    name, extension = filename.rsplit(".", 1)

    # Convert the extension to lowercase.
    extension = extension.lower()

    # Return whether the extension is allowed.
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
    """
    Validate that an uploaded file exists and is a supported CSV file.

    Args:
        file: The uploaded file object from Flask's request.files.

    Returns:
        True if the file is valid.

    Raises:
        ValueError: If the file is missing or has an invalid extension.
    """

    # Check that a file was uploaded.
    if file is None:
        raise ValueError("No file was uploaded.")

    # Check that the filename exists.
    if not file.filename:
        raise ValueError("Please select a file to upload.")

    # Remove leading and trailing whitespace.
    filename = file.filename.strip()

    # Check that the filename is not empty.
    if not filename:
        raise ValueError("Please select a file to upload.")

    # Check that the file has an allowed extension.
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

def validate_columns(dataframe, x_column, y_column, error_column=None):
    """
    Validate selected columns and return a cleaned copy of the data.

    Args:
        dataframe: pandas DataFrame containing the uploaded data.
        x_column: Name of the selected X-axis column.
        y_column: Name of the selected Y-axis column.
        error_column: Optional name of the error-bar column.

    Returns:
        A cleaned pandas DataFrame containing the selected columns.

    Raises:
        ValueError: If the selections or data are invalid.
    """

    # Check that a dataset is available.
    if dataframe is None or dataframe.empty:
        raise ValueError("The dataset is not available.")

    # Check that an X-axis column was selected.
    if x_column is None or not str(x_column).strip():
        raise ValueError("An X-axis column is required.")

    # Check that a Y-axis column was selected.
    if y_column is None or not str(y_column).strip():
        raise ValueError("A Y-axis column is required.")

    # Clean the selected column names.
    x_column = str(x_column).strip()
    y_column = str(y_column).strip()

    if error_column is not None:
        error_column = str(error_column).strip()

        if not error_column:
            error_column = None

    # Check that the selected columns exist.
    if x_column not in dataframe.columns:
        raise ValueError(
            f"The selected X-axis column '{x_column}' was not found."
        )

    if y_column not in dataframe.columns:
        raise ValueError(
            f"The selected Y-axis column '{y_column}' was not found."
        )

    if error_column is not None and error_column not in dataframe.columns:
        raise ValueError(
            f"The selected error-bar column '{error_column}' was not found."
        )

    # Check that X and Y are different columns.
    if x_column == y_column:
        raise ValueError("X and Y must use different columns.")

    # Create a list of the selected columns.
    selected_columns = [x_column, y_column]

    if error_column is not None:
        selected_columns.append(error_column)

    # Create a copy containing only the selected columns.
    df_copy = dataframe[selected_columns].copy()

    # Convert the Y column to numeric values.
    df_copy[y_column] = pd.to_numeric(
        df_copy[y_column],
        errors="coerce"
    )

    # Convert the optional error column to numeric values.
    if error_column is not None:
        df_copy[error_column] = pd.to_numeric(
            df_copy[error_column],
            errors="coerce"
        )

    # Attempt to convert the X column to numeric values.
    numeric_x = pd.to_numeric(
        df_copy[x_column],
        errors="coerce"
    )

    # Use numeric X values only if every nonmissing X value converted.
    if numeric_x.notna().sum() == df_copy[x_column].notna().sum():
        df_copy[x_column] = numeric_x

    # Remove rows with missing X or Y values.
    required_columns = [x_column, y_column]

    if error_column is not None:
        required_columns.append(error_column)

    df_copy = df_copy.dropna(subset=required_columns)

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
      
    if value is None:
          return None
    value = str(value).strip()

    # Remove leading and trailing whitespace.
    value = str('value').strip()

    if not value:
      return None

    # Try to convert the value into a float.
    try:
      return float(value)

    except ValueError:
      raise ValueError ("field name must be a valid number)




def parse_positive_integer(value, field_name, default=None):
    if value is None:
      return default

    value = str(value).strip()

  
    if not value:
      return default

    # Try to convert value into an integer.
    try:
      return int(value)
    except ValueError:
      raise ValueError (f"{field_name} must be a whole number")
    
    if value <= 0:
      raise ValueError (f {<field_name} must begreater than zero")
    
    return value
