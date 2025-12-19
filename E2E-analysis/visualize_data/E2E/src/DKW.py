import numpy as np

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