import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import argparse
from scipy.stats import expon

def hyperexp_pdf(x, params):
    """
    Calculates the PDF of a hyper-exponential distribution.
    params: list of p1, rate1, p2, rate2, ...
    """
    pdf = np.zeros_like(x, dtype=float)
    for i in range(0, len(params), 2):
        p = params[i]
        rate = params[i+1]
        pdf += p * rate * np.exp(-rate * x)
    return pdf

def hyperexp_cdf(x, params):
    """
    Calculates the CDF of a hyper-exponential distribution.
    params: list of p1, rate1, p2, rate2, ...
    """
    cdf = np.zeros_like(x, dtype=float)
    for i in range(0, len(params), 2):
        p = params[i]
        rate = params[i+1]
        cdf += p * (1 - np.exp(-rate * x))
    return cdf

def hypoexp_pdf(x, rates):
    """
    Calculates the PDF of a hypo-exponential distribution for distinct rates.
    rates: list of rates [rate1, rate2, ...]
    """
    k = len(rates)
    pdf = np.zeros_like(x, dtype=float)
    for i in range(k):
        li = rates[i]
        prod_term = 1.0
        for j in range(k):
            if i != j:
                lj = rates[j]
                prod_term *= lj / (lj - li)
        pdf += li * np.exp(-li * x) * prod_term
    return pdf

def hypoexp_cdf(x, rates):
    """
    Calculates the CDF of a hypo-exponential distribution for distinct rates.
    rates: list of rates [rate1, rate2, ...]
    """
    k = len(rates)
    cdf = np.ones_like(x, dtype=float)
    for i in range(k):
        li = rates[i]
        prod_term = 1.0
        for j in range(k):
            if i != j:
                lj = rates[j]
                prod_term *= lj / (lj - li)
        cdf -= np.exp(-li * x) * prod_term
    return cdf

def main():
    parser = argparse.ArgumentParser(description='Plot real and theoretical distributions.')
    parser.add_argument('--file-path', required=True, help='Path to the CSV file with real execution times.')
    parser.add_argument('--dist-type', required=True, choices=['hypoexp', 'hyperexp'], help='Type of theoretical distribution.')
    parser.add_argument('--params', required=True, type=float, nargs='+', help='Parameters for the theoretical distribution.')
    parser.add_argument('--output-file', default='comparison_plot.pdf', help='Path to save the output plot.')

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File '{args.file_path}' not found.")
        sys.exit(1)

    print(f"Reading real data from: {args.file_path}")
    df_real = pd.read_csv(args.file_path)

    if 'execution_time_ms' not in df_real.columns:
        print(f"Error: '{args.file_path}' must contain 'execution_time_ms' column.")
        sys.exit(1)

    real_times = df_real['execution_time_ms'].sort_values()

    # Empirical CDF for real data
    cdf_real = np.arange(1, len(real_times) + 1) / len(real_times)

    # Time range for theoretical plot
    x_theory = np.linspace(0, real_times.max(), 1000)

    if args.dist_type == 'hyperexp':
        if len(args.params) % 2 != 0:
            print("Error: Hyper-exponential distribution requires pairs of p_i and rate_i.")
            sys.exit(1)
        if not np.isclose(sum(args.params[::2]), 1.0):
            print("Error: Probabilities for hyper-exponential must sum to 1.")
            sys.exit(1)
        pdf_theory = hyperexp_pdf(x_theory, args.params)
        cdf_theory = hyperexp_cdf(x_theory, args.params)
        dist_name = "Hyper-exponential"
    elif args.dist_type == 'hypoexp':
        pdf_theory = hypoexp_pdf(x_theory, args.params)
        cdf_theory = hypoexp_cdf(x_theory, args.params)
        dist_name = "Hypo-exponential"

    # Plotting
    plt.figure(figsize=(14, 6))

    # CDF plot
    plt.subplot(1, 2, 1)
    plt.plot(real_times, cdf_real, label='Real CDF', color='blue')
    plt.plot(x_theory, cdf_theory, label=f'Theoretical CDF', color='red')
    plt.xlabel('Time (ms)')
    plt.ylabel('CDF')
    plt.title('Cumulative Distribution Function')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # PDF plot
    plt.subplot(1, 2, 2)
    plt.hist(real_times, bins=100, density=True, alpha=0.6, color='blue', label='Real CDF')
    plt.plot(x_theory, pdf_theory, label=f'Theoretical PDF', color='red')
    plt.xlabel('Time (ms)')
    plt.ylabel('Density')
    plt.title('Probability Density Function')
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.suptitle(f'users/reserve Distribution Function', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    plt.savefig(args.output_file)
    print(f"Plot saved to {args.output_file}")

if __name__ == '__main__':
    main()