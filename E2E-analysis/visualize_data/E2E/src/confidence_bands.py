import numpy as np
from scipy.stats import beta

def DKW_confidence_bands(n, alpha=0.05):
    """
    Computes the Dvoretzky-Kiefer-Wolfowitz (DKW) confidence simultaneus bands for the CDF of a sample of size n.
    Args:
        n (int): The sample size.
        alpha (float): The significance level (default 0.05 for 95% confidence).
    Returns:
        tuple: Two numpy arrays (lower, upper) of length n representing the confidence bands.
    """
    epsilon = np.sqrt(np.log(2 / alpha) / (2 * n))
    ecdf = np.arange(1, n + 1) / n
    lower = np.maximum(ecdf - epsilon, 0)
    upper = np.minimum(ecdf + epsilon, 1)
    return lower, upper

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

def bootstrap_confidence_bands(n, alpha=0.05, n_boot=5000):
    """
    Computes bootstrapping confidence intervals for the CDF of a sample of size n.
    Args:
        n (int): The sample size.
        alpha (float): The significance level (default 0.05 for 95% confidence).
        n_boot (int): Number of bootstrap resamples (default 5000).
    Returns:
        tuple: Two numpy arrays (lower, upper) of length n representing the confidence bands.
    """
    ecdf_orig = np.arange(1, n + 1) / n
    resampled_counts = np.random.multinomial(n, [1/n] * n, size=n_boot)
    bootstrap_ecdfs = np.cumsum(resampled_counts, axis=1) / n
    max_deviations = np.max(np.abs(bootstrap_ecdfs - ecdf_orig), axis=1)
    critical_value = np.percentile(max_deviations, 100 * (1 - alpha))
    lower = np.maximum(ecdf_orig - critical_value, 0)
    upper = np.minimum(ecdf_orig + critical_value, 1)
    return lower, upper