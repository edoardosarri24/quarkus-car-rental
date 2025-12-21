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

def bootstrap_confidence_bands(data, alpha=0.05, n_boot=10000, method='pointwise'):
    """
    Computes Bootstrap confidence bands for the Empirical Cumulative Distribution Function (ECDF).
    Args:
        data (array-like): The original input sample.
        alpha (float): Significance level (e.g., 0.05 for 95% confidence).
        n_boot (int): Number of bootstrap resamples to perform.
        method (str): 'pointwise' for local bands, 'simultaneous' for global bands.
    Returns:
        tuple: (lower, upper, ecdf_orig) numpy arrays containing the lower bound, upper bound, and the original ECDF values.
    """
    n = len(data)
    data_sorted = np.sort(data)
    ecdf_orig = np.arange(1, n + 1) / n
    counts = np.random.multinomial(n, [1/n] * n, size=n_boot)
    boot_ecdfs = np.cumsum(counts, axis=1) / n
    if method == 'pointwise':
        lower = np.percentile(boot_ecdfs, 100 * (alpha / 2), axis=0)
        upper = np.percentile(boot_ecdfs, 100 * (1 - alpha / 2), axis=0)
    elif method == 'simultaneous':

        distances = np.abs(boot_ecdfs - ecdf_orig)
        max_distances = np.max(distances, axis=1)
        d_alpha = np.percentile(max_distances, 100 * (1 - alpha))
        lower = np.clip(ecdf_orig - d_alpha, 0, 1)
        upper = np.clip(ecdf_orig + d_alpha, 0, 1)
    else:
        raise ValueError("Unknown method. Please use 'pointwise' or 'simultaneous'.")
    return lower, upper, ecdf_orig