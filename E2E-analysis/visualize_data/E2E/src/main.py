import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import traceback
from dominance import pairwise_dominance
from confidence_bands import *

"""
Script to visualize E2E execution time distribution.
Usage:
    python main.py
"""
def main(band_type, alpha):
    # define the paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eulero_file = os.path.join(script_dir, '../input_file/eulero_CDF.csv')
    real_file = os.path.join(script_dir, '../input_file/real_e2e_execution_time.csv')
    output_file = os.path.join(script_dir, '../results/compare_e2e_distribution.pdf')
    if not os.path.exists(eulero_file) or not os.path.exists(real_file):
        print(f"Error: Files not found.\nLooking for:\n{eulero_file}\n{real_file}")
        sys.exit(1)

    try:
        # read the data
        df_eulero = pd.read_csv(eulero_file)
        df_real = pd.read_csv(real_file)
        if not {'time', 'cdf'}.issubset(df_eulero.columns):
            print(f"Error: '{eulero_file}' must contain 'time' and 'cdf' columns.")
            sys.exit(1)
        if 'duration_ms' not in df_real.columns:
            print(f"Error: '{real_file}' must contain 'duration_ms' column.")
            sys.exit(1)

        # eulero pdf
        dt_eulero = df_eulero['time'].diff()
        dcdf_eulero = df_eulero['cdf'].diff()
        pdf_eulero = dcdf_eulero / dt_eulero
        pdf_eulero = pdf_eulero.fillna(0)

        # real cdf
        real_times = df_real['duration_ms'].sort_values()
        n_real = len(real_times)
        cdf_real = np.arange(1, n_real + 1) / n_real

        # Confidence bands
        lower_band, upper_band = None, None
        band_label = ""
        if band_type == 'cp':
            lower_band, upper_band = clopperPearson_confidence_bands(n_real, alpha=alpha)
            band_label = f'{int((1-alpha)*100)}% Confidence Band (CP)'
        elif band_type == 'dkw':
            lower_band, upper_band = DKW_confidence_bands(n_real, alpha=alpha)
            band_label = f'{int((1-alpha)*100)}% Confidence Band (DKW)'
        elif band_type == 'bootstrap':
            lower_band, upper_band = bootstrap_confidence_bands(n_real, alpha=alpha)
            band_label = f'{int((1-alpha)*100)}% Confidence Band (bootstrapping)'

        # dominance
        n_samples = 1000000
        random_probs = np.random.rand(n_samples)
        eulero_synthetic_samples = np.interp(random_probs, df_eulero['cdf'], df_eulero['time'])
        dom_val = pairwise_dominance(real_times.values, eulero_synthetic_samples)

        # absolute difference area (MAE)
        t_min = min(df_eulero['time'].min(), real_times.min())
        t_max = max(df_eulero['time'].max(), real_times.max())
        common_grid = np.linspace(t_min, t_max, 10000)
        cdf_real_interp = np.interp(common_grid, real_times, cdf_real)
        cdf_eulero_interp = np.interp(common_grid, df_eulero['time'], df_eulero['cdf'])
        abs_diff = np.abs(cdf_real_interp - cdf_eulero_interp)
        if hasattr(np, 'trapezoid'):
            cdf_diff_area = np.trapezoid(abs_diff, common_grid)
        else:
            cdf_diff_area = np.trapz(abs_diff, common_grid)
        mae = cdf_diff_area

        # Squared difference area (MSE)
        quantiles_for_error = (np.arange(n_real) + 0.5) / n_real
        eulero_samples_for_error = np.interp(quantiles_for_error, df_eulero['cdf'], df_eulero['time'])
        mse = np.mean((real_times.values - eulero_samples_for_error) ** 2)

        # plotting CDF
        plt.figure(figsize=(14, 6))
        plt.subplot(1, 2, 1)
        plt.plot(real_times, cdf_real, label='Real CDF', color='red', linewidth=2)
        if band_type != 'none':
            plt.fill_between(real_times, lower_band, upper_band, color='red', alpha=0.2, label=band_label)
        plt.plot(df_eulero['time'], df_eulero['cdf'], label='Eulero (Approx) CDF', color='blue', linewidth=2)
        plt.fill_between(common_grid, cdf_real_interp, cdf_eulero_interp, color='gray', alpha=0.2, label='Diff Area')
        textstr = '\n'.join((
            f'Dominance: {dom_val:.4f}',
            f'absolute difference area (MAE): {mae:.4f}',
            f'Squared difference area (MSE): {mse:.4f}'
        ))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(0.4, 0.15, textstr, transform=plt.gca().transAxes, fontsize=12,
                verticalalignment='top', bbox=props)
        plt.xlabel('Time (ms)')
        plt.ylabel('CDF')
        plt.title('Cumulative Distribution Function (CDF)')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # plotting PDF
        plt.subplot(1, 2, 2)
        plt.hist(real_times, bins=500, density=True, alpha=0.5, color='red', label='Real PDF (Histogram)')
        plt.plot(df_eulero['time'], pdf_eulero, label='Eulero (Approx) PDF', color='blue', linewidth=2)
        plt.xlabel('Time (ms)')
        plt.ylabel('Probability Density')
        plt.title('Probability Density Function (PDF)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.suptitle('Comparison of E2E Execution Time Distribution', fontsize=16)
        plt.tight_layout()

        # Save the plot
        plt.savefig(output_file)
        print(f"Visualization saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Choose:
    # band_type = 'cp'
    # band_type = 'dkw'
    band_type = 'bootstrap'
    main(band_type, alpha = 0.01)