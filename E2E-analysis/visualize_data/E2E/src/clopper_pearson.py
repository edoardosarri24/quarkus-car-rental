import numpy as np
from scipy.stats import beta

def clopperPearson_confidence_bands(n, alpha=0.05):
    """
    Computes pointwise Clopper-Pearson confidence intervals for the CDF of a sample of size n.
    Args:
        n (int): The sample size.
        alpha (float): The significance level (default 0.05 for 95% confidence).
    Returns:
        tuple: Two numpy arrays (lower, upper) of length n representing the confidence bands.
    """
    k = np.arange(1, n + 1)
    # L = Beta(alpha/2, k, n - k + 1)
    lower = beta.ppf(alpha / 2, k, n - k + 1)
    # U = Beta(1 - alpha/2, k + 1, n - k)
    upper = np.ones(n)
    mask = k < n
    if np.any(mask):
        upper[mask] = beta.ppf(1 - alpha / 2, k[mask] + 1, n - k[mask])
    return lower, upper