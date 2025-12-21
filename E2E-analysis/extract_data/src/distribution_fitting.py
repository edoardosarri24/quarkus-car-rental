import math

def fit_hyper_exponential(mu: float, cv: float):
    """
    Calculates the parameters of a 2-phase Hyper-exponential distribution.
    Args:
        mu (float): The average.
        cv (float): The coefficient of variation (sigma / mean). Must be >= 1.0.
    Returns:
        tuple: (p1, lambda1, p2, lambda2)
    Raises:
        ValueError: If cv < 1.0 (use Hyper-exponential or generalized-erlang).
    """
    if cv < 1.0:
        raise ValueError(
            f"CV ({cv}) < 1.0. For low variance, use the hypo-exponential distribution or ."
        )
    term = math.sqrt((cv**2 - 1) / (cv**2 + 1))
    p1 = 0.5 * (1 + term)
    p2 = 1 - p1
    lambda1 = (2 * p1) / mu
    lambda2 = (2 * p2) / mu
    return p1, lambda1, p2, lambda2

def fit_hypo_exponential(mu: float, cv: float):
    """
    Calculates the parameters of a 2-phase Hypo-exponential distribution.
    Args:
        mu (float): The average.
        cv (float): The coefficient of variation. Must be between 1/sqert(2) and 1.0.
    Returns:
        tuple: (lambda1, lambda2) - The rates of the two sequential phases.
    Raises:
        ValueError: If cv >= 1.0 (use Hyper-exponential).
        ValueError: If cv < 1/sqrt(2) (use generalized-erlang).
    """
    if cv >= 1.0:
        raise ValueError(
            f"CV ({cv}) >= 1.0. For high variance, use the Hyper-exponential distribution."
        )
    if cv < 1/math.sqrt(2):
        raise ValueError(
            f"CV ({cv}) < 1/sqrt(2). For low variance, use the generalized-erlang distribution."
        )
    discriminant = math.sqrt(mu**2 * (2 * (cv**2) - 1))
    mu1 = (mu + discriminant) / 2
    mu2 = (mu - discriminant) / 2
    lambda1 = 1.0 / mu1
    lambda2 = 1.0 / mu2
    return lambda1, lambda2

def fit_generalized_erlang(mu: float, cv: float):
    """
    Calculates the parameters of Generalized Erlang distribution (Erlang-k + Exponential).
    Args:
        mu (float): The mean.
        cv (float): The coefficient of variation (sigma / mean). Must be < 1/sqrt(2).
    Returns:
        tuple: (k_erlang, lambda1, lambda2): the distribution is Sum(k_erlang * Exp(lambda1)) + Exp(lambda2).
    Raises:
        ValueError: If cv > 1/sqrt(2) (use Hypo-exponential or Hyper-exponential).
    """
    if cv >= 1/math.sqrt(2):
        raise ValueError(
            f"CV ({cv}) > 1/sqrt(2). For more high variance, use the hypo-exponential or hyper-exponential distribution."
        )
    n_total = math.ceil(1 / (cv**2))
    k = n_total - 1
    A = k * (k + 1)
    B = -2 * mu * k
    C = (mu**2) * (1 - cv**2)
    delta = B**2 - 4 * A * C
    if delta < -1e-12:
        raise ValueError("Complex roots: inconsistent CV or numerical issue.")
    delta = max(delta, 0.0)
    sqrt_delta = math.sqrt(delta)
    x1 = (-B - sqrt_delta) / (2 * A)
    x2 = (-B + sqrt_delta) / (2 * A)
    candidates = []
    for x in (x1, x2):
        if x > 0:
            y = mu - k * x
            if y > 0:
                candidates.append((x, y))
    if not candidates:
        raise ValueError("No positive solution found for (lambda1, lambda2).")
    x, y = candidates[0]
    return k, 1/x, 1/y

def fit_distribution(mean: float, cv: float):
    """
    Decides which distribution to fit based on the coefficient of variation (CV).
    Args:
        mean (float): The mean of the distribution.
        cv (float): The coefficient of variation.
    Returns:
        dict: A dictionary containing the distribution type and its parameters.
    """
    if cv >= 1.0:
        p1, lambda1, p2, lambda2 = fit_hyper_exponential(mean, cv)
        return {
            "type": "Hyper-exponential",
            "params": {
                "p1": p1,
                "lambda1": lambda1,
                "p2": p2,
                "lambda2": lambda2
            },
            "java_code": f'new HyperExponentialTime(new BigDecimal({lambda1}), new BigDecimal({lambda2}), new BigDecimal({p1}))'
        }
    elif cv >= 1/math.sqrt(2):
        lambda1, lambda2 = fit_hypo_exponential(mean, cv)
        return {
            "type": "Hypo-exponential",
            "params": {
                "lambda1": lambda1,
                "lambda2": lambda2
            },
            "java_code": f'new HypoExponentialTime(new BigDecimal({lambda1}), new BigDecimal({lambda2}))'
        }
    else:
        k, lambda1, lambda2 = fit_generalized_erlang(mean, cv)
        return {
            "type": "Generalized-Erlang",
            "params": {
                "k": k,
                "lambda1": lambda1,
                "lambda2": lambda2
            },
            "java_code": f'new GeneralizeErlangTime({k}, new BigDecimal({lambda1}), new BigDecimal({lambda2}))'
        }