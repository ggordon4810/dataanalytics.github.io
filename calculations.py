import numpy as np
import scipy
from numpy.polynomial import Polynomial

def calculate_mean(values):
   # Check that values was provided.
    if values is None:
      raise ValueError ("Value is required.")   

    arr = np.array(values, dtype=float)

    cleaned_arr = arr[~np.isnan(arr)]
    
    if len(cleaned_arr) == 0::
      raise ValueError ("Numeric data is required")

    Calculate the arithmetic mean.
    total = 0
    for i in range (len(cleaned_arr)):
      total += cleaned_arr[i]

    mean = total / len(cleaned_arr)
    return float(mean)

def calculate_standard_deviation(values):

    if values is None:
      raise ValueError ("Value is required.")   

    arr = np.array(values, dtype=float)

    cleaned_arr = arr[~np.isnan(arr)]

    if len(cleaned_arr) < 2:
      raise ValueError ("At least two values are required.")
    mean = calculate_mean(cleaned_arr)
    total = 0
    for i in range(len(cleaned_arr)):
      total += (cleaned_arr[i] - mean) ** 2
    
    standard_dev = np.sqrt(total / (len(cleaned_arr) - 1))

    return float(standard_dev)

def calculate_standard_error(values):

    if values is None:
      raise ValueError ("Value is required.")   

    arr = np.array(values, dtype=float)

    cleaned_arr = arr[~np.isnan(arr)]

    if len(cleaned_arr) < 2:
      raise ValueError ("At least two values are required.")

    std = calculate_standard_deviation(cleaned_arr)

    std_err = std / np.sqrt(len(cleaned_arr))

    return float(std_err)

def calculate_r_squared(actual_values, predicted_values):
    actual = np.array(actual_values, dtype=float)
    predict = np.array(predicted_values, dtype=float)

    if len(actual) != len(predict):
      raise ValueError ("There should be the same amount of actual and predicted values.")

    if len(actual) < 2:
      raise ValueError ("At least two values are required.")
    
    actual_mean = calculate_mean(actual)

    sumofsq = 0

    for i in range (len(actual)):
      sumofsq += (actual[i] - actual_mean) ** 2

    ressumofsq = 0
    for i in range (len(actual)):
      ressumofsq += (actual[i] - predict[i]) ** 2

    if sumofsq == 0:
     return 0.0

    else:
     r_squared = 1 - (ressumofsq / sumofsq)

    return float(r_squared)


def calculate_linear_regression(x_values, y_values):

    if x_values is None:
      raise ValueError ("An x value is required.")
      
    if y_values is None:
      raise ValueError ("A y value is required.")

    x_values = np.array (x_values, dtype=float)
    y_values = np.array (y_values, dtype=float)

    if len(x_values) != len(y_values):
      raise ValueError ("There should be the same amount of x and y values.")

    if len(x_values) < 2:
      raise ValueError ("At least two x and y values are required.")

    if len(set(x_values)) < 2:
      raise ValueError ("Regression cannot be calculated without different X values.")


    line_fit = Polynomial.fit(x_values, y_values, deg=1)
    
    intercept, slope = line_fit.convert().coef

    predicted_y_values = []
    for i in range(len(x_values)):
      y = slope * x_values[i] + intercept
      predicted_y_values.append(y)

    r_squared = calculate_r_squared(y_values, predicted_y_values)

    values = {
      "slope": float(slope),
      "intercept": float(intercept),
      "r_squared": r_squared,
      "predicted_values": predicted_y_values,
      } 
    return values

def generate_regression_line(
    x_values,
    slope,
    intercept,
    number_of_points = 100
):
    if number_of_points < 2:
      raise ValueError("At least two regression-line points are required.")
    if x_values is None:
      raise ValueError("X values are required.")
    x_values = np.array (x_values, dtype=float)
    
    if len(x_values) < 2:
      raise ValueError ("At least two x values are required.")

    min_x = np.min(x_values)

    max_x = np.max(x_values)

    regression_x = np.linspace(min_x, max_x, number_of_points)

    regression_y = []

    for i in range (len(regression_x)):
      y = slope * regression_x[i] + intercept
      regression_y.append(y)

    regression_values = {
      "regression_x": regression_x,
      "regression_y": regression_y,
    }
    return regression_values

def calculate_confidence_interval(
    values,
    confidence = 0.95
):

    arr = np.array(values, dtype=float)

    cleaned_arr = arr[~np.isnan(arr)]

    if len(cleaned_arr) < 2:
      raise ValueError("At least two measurements are required.")

    #Check that confidence is greater than 0 and less than 1.
    if not 0 < confidence < 1:
      raise ValueError("Confidence must be between zero and one.")
    
    # Calculate the sample size.
    sample_size = len(cleaned_arr)
    
    # Degrees of freedom.
    degrees_of_freedom = sample_size - 1
    
    # Calculate the mean.
    mean = calculate_mean(cleaned_arr)
    
    # Calculate the standard error.
    standard_error = calculate_standard_error(cleaned_arr)
    
    # Calculate the two-tailed critical t value.
    alpha = 1 - confidence
    
    critical_t = scipy.stats.t.ppf(
        1 - alpha / 2,
        degrees_of_freedom
    )
    
    # Calculate the margin of error.
    margin_of_error = critical_t * standard_error
    
    # Calculate the confidence interval bounds.
    lower_bound = mean - margin_of_error
    upper_bound = mean + margin_of_error
    
    # Return the results.
    results = {
        "mean": float(mean),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "margin_of_error": float(margin_of_error),
        "confidence": float(confidence),
    }

    return results

def summarize_numeric_data(values):

    arr = np.array(values, dtype=float)

    cleaned_arr = arr[~np.isnan(arr)]

    if len(cleaned_arr) == 0:
        raise ValueError("Numeric values are required.")

    count = len(cleaned_arr)

    minimum = min(cleaned_arr)
    maximum = max(cleaned_arr)
    mean = calculate_mean(cleaned_arr)

    if count >=2:
      standard_deviation = calculate_standard_deviation(cleaned_arr)
      standard_error = calculate_standard_error(cleaned_arr)
    else:
      standard_deviation = None
      standard_error = None
    results = {
        "count": (count),
        "minimum": float(minimum),
        "maximum": float(maximum),
        "mean": float(mean),
        "standard_deviation": (standard_deviation),
        "standard_error": (standard_error),
    }
    
    return(results)
