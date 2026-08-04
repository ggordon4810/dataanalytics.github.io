import os
import uuid

import pandas as pd

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"csv"} 

def allowed_file(filename):
  
    If filename is not a string:
        Return False.

    If filename does not contain a period:
        Return False.

    Split the filename at the final period.

    Take the extension after the final period.

    Convert the extension to lowercase.

    If the extension is inside ALLOWED_EXTENSIONS:
        Return True.

    Otherwise:
        Return False.
def generate_safe_filename(filename):
  Use secure_filename on the original filename.

    If the safe filename is empty:
        Raise a ValueError saying the filename is invalid.

    Separate the safe filename into:
        base filename
        extension

    Create a unique identifier using uuid.uuid4.

    Convert the UUID to a string.

    Build a new filename using:
        base filename
        underscore
        unique identifier
        extension

    Return the new filename.
def validate_uploaded_file(file):
    If file is None:
        Raise a ValueError saying no file was uploaded.

    Get file.filename.

    If the filename is missing or empty:
        Raise a ValueError saying the user must select a file.

    Remove whitespace from the filename.

    If the filename is empty after removing whitespace:
        Raise a ValueError saying the user must select a file.

    Use allowed_file to check the filename.

    If allowed_file returns False:
        Raise a ValueError saying only CSV files are supported.

    Return True.

def read_csv_file(filepath):
 Check whether filepath exists using os.path.exists.

    If the file does not exist:
        Raise a ValueError saying the uploaded file could not be found.

    Try to read the CSV using pandas.read_csv.

    If pandas reports that the file is empty:
        Raise a ValueError saying the CSV file is empty.

    If pandas cannot parse the file:
        Raise a ValueError saying the CSV could not be read.

    If another file-reading error occurs:
        Raise a ValueError with a general file-reading message.

    Check whether the DataFrame has zero rows.

    If it has zero rows:
        Raise a ValueError saying the CSV contains no data rows.

    Check whether the DataFrame has fewer than two columns.

    If it has fewer than two columns:
        Raise a ValueError saying the CSV must contain at least two columns.

    Remove leading and trailing whitespace from every column name.

    Check for blank column names.

    If any column name is blank:
        Raise a ValueError saying every column must have a name.

    Check whether any column names are duplicated.

    If duplicate names exist:
        Raise a ValueError saying every column name must be unique.

    Return the DataFrame.

def validate_columns(dataframe, x_column, y_column, error_column=None):
 If dataframe is None:
        Raise a ValueError saying no dataset is available.

    If x_column is missing or empty:
        Raise a ValueError saying an X-axis column is required.

    If y_column is missing or empty:
        Raise a ValueError saying a Y-axis column is required.

    Remove whitespace from x_column and y_column.

    If error_column was provided:
        Remove whitespace from error_column.

    Check whether x_column exists in dataframe.columns.

    If it does not:
        Raise a ValueError saying the selected X column was not found.

    Check whether y_column exists in dataframe.columns.

    If it does not:
        Raise a ValueError saying the selected Y column was not found.

    If x_column and y_column are the same:
        Raise a ValueError saying X and Y must use different columns.

    If error_column was provided:
        Check whether it exists in dataframe.columns.

        If not:
            Raise a ValueError saying the selected error column was not found.

    Create a copy containing the selected X and Y columns.

    If error_column was provided:
        Include it in the copied data.

    Convert the Y column to numeric values.
    Invalid values should become missing values.

    If an error column was provided:
        Convert the error column to numeric values.
        Invalid values should become missing values.

    For the X column:
        Attempt numeric conversion.

        If every converted X value is valid:
            Use the numeric version.

        Otherwise:
            Keep the original X values as categories.

    Remove rows where X or Y is missing.

    If an error column is being used:
        Also remove rows where the error value is missing.

    If fewer than two valid rows remain:
        Raise a ValueError saying at least two valid measurements are required.

    If any error-bar value is negative:
        Raise a ValueError saying error-bar values cannot be negative.

    Return the cleaned dataset.

def parse_optional_float(value, field_name):
      
    If value is None:
        Return None.

    Convert value to a string if necessary.

    Remove leading and trailing whitespace.

    If the remaining value is empty:
        Return None.

    Try to convert the value into a float.

    If conversion fails:
        Raise a ValueError saying:
        "<field_name> must be a valid number."

    Return the float.

def parse_positive_integer(value, field_name, default=None):
       If value is None:
        Return default.

    Convert value to a string.

    Remove whitespace.

    If value is empty:
        Return default.

    Try to convert value into an integer.

    If conversion fails:
        Raise a ValueError saying:
        "<field_name> must be a whole number."

    If the integer is less than or equal to zero:
        Raise a ValueError saying:
        "<field_name> must be greater than zero."

    Return the integer.
