import math

def fit_hypo_exponential(mu: float, cv: float):
    """
    Calculates the parameters of a 2-phase Hypo-exponential distribution.
    Args:
        mu (float): The average execution time (E[X]).
        cv (float): The coefficient of variation.
                    Must be between ~0.707 and 1.0.
    Returns:
        tuple: (lambda1, lambda2) - The rates of the two sequential phases.
    Raises:
        ValueError: If cv >= 1.0 (use Hyper-exponential).
        ValueError: If cv < 0.707 (impossible with only 2 phases, Erlang-k is needed).
    """
    if cv >= 1.0:
        raise ValueError(
            f"CV ({cv}) >= 1.0. For high variance, use the Hyper-exponential distribution."
        )
    if cv**2 < 0.5:
        raise ValueError(
            f"CV ({cv}) is too low for a 2-phase Hypo-exponential (min ~0.707). "
            "The data requires a higher-order Erlang distribution (k > 2)."
        )
    discriminant = math.sqrt(mu**2 * (2 * (cv**2) - 1))
    mu1 = (mu + discriminant) / 2
    mu2 = (mu - discriminant) / 2
    lambda1 = 1.0 / mu1
    lambda2 = 1.0 / mu2
    return lambda1, lambda2

def fit_hyper_exponential(mu: float, cv: float):
    """
    Calculates the parameters of a 2-phase Hyper-exponential distribution (H2)
    based on the 'Balanced Means' method.
    Args:
        mu (float): The average execution time (E[X]).
        cv (float): The coefficient of variation (sigma / mean). Must be >= 1.0 for an H2 distribution.
    Returns:
        tuple: (p1, lambda1, p2, lambda2)
    Raises:
        ValueError: If cv < 1.0 (Data not compatible with H2).
    """
    if cv < 1.0:
        raise ValueError(
            f"The coefficient of variation ({cv}) is < 1. "
            "The Hyper-exponential distribution requires CV >= 1. "
            "Consider using an Erlang or Hypo-exponential distribution."
        )
    term = math.sqrt((cv**2 - 1) / (cv**2 + 1))
    p1 = 0.5 * (1 + term)
    p2 = 1 - p1
    lambda1 = (2 * p1) / mu
    lambda2 = (2 * p2) / mu
    return p1, lambda1, p2, lambda2

def fit_erlang(mu: float, cv: float):
    """
    Calculates the parameters of an Erlang distribution using the method of moments.
    Args:
        mu (float): The average execution time (E[X]).
        cv (float): The coefficient of variation (sigma / mean).
                    Must be <= 1.0 for an Erlang distribution.
    Returns:
        tuple: (k, lambda) - The integer shape parameter (k) and the rate (lambda).
    Raises:
        ValueError: If cv > 1.0 (data not compatible, consider Hyper-exponential).
    """
    if cv > 1.0:
        raise ValueError(
            f"The coefficient of variation ({cv}) is > 1. "
            "The Erlang distribution requires CV <= 1. "
            "Consider using a Hyper-exponential distribution."
        )
    # For an Erlang distribution, the squared coefficient of variation is 1/k.
    k = round(1.0 / (cv**2))
    # The mean is k / lambda.
    lambda_rate = k / mu
    return int(k), lambda_rate