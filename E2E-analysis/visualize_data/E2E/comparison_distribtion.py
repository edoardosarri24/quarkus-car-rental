import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def main():
    # Define file paths
    approx_file = 'approxCDF.csv'
    real_file = 'real_E2E_execTime.csv'
    output_file = 'results/E2E distribution function.pdf'

    # Check if files exist
    if not os.path.exists(approx_file) or not os.path.exists(real_file):
        print(f"Error: Both '{approx_file}' and '{real_file}' must exist in the current directory.")
        sys.exit(1)

    print(f"Reading data from: {approx_file} and {real_file}")

    try:
        # Read the CSV files
        df_approx = pd.read_csv(approx_file)
        df_real = pd.read_csv(real_file)

        # Check required columns
        if not {'time', 'cdf'}.issubset(df_approx.columns):
            print(f"Error: '{approx_file}' must contain 'time' and 'cdf' columns.")
            sys.exit(1)

        if 'execution_time_ms' not in df_real.columns:
            print(f"Error: '{real_file}' must contain 'execution_time_ms' column.")
            sys.exit(1)

        # Calculate PDF (Derivative of CDF) for Approx
        # PDF = diff(cdf) / diff(time)
        dt_approx = df_approx['time'].diff()
        dcdf_approx = df_approx['cdf'].diff()
        pdf_approx = dcdf_approx / dt_approx

        # Prepare Real Data
        real_times = df_real['execution_time_ms'].sort_values()
        # Empirical CDF
        cdf_real = np.arange(1, len(real_times) + 1) / len(real_times)

        # Plotting
        plt.figure(figsize=(14, 6))

        # Plot CDF Comparison
        plt.subplot(1, 2, 1)
        plt.plot(real_times, cdf_real, label='Real CDF', color='blue')
        plt.plot(df_approx['time'], df_approx['cdf'], label='Approx CDF', color='red')
        plt.xlabel('Time (ms)')
        plt.ylabel('CDF')
        plt.title('Cumulative Distribution Function')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Plot PDF/Histogram Comparison
        plt.subplot(1, 2, 2)
        # Plot histogram of real data
        plt.hist(real_times, bins=500, density=True, alpha=0.6, color='blue', label='Real PDF')
        # Plot approx PDF
        plt.plot(df_approx['time'], pdf_approx, label='Approx PDF', color='red')
        plt.xlabel('Time (ms)')
        plt.ylabel('Density')
        plt.title('Probability Density Function')
        plt.grid(True, alpha=0.3)
        plt.legend()

        plt.suptitle('E2E Distribution Function', fontsize=16)
        plt.tight_layout()

        # Save the plot
        # Ensure results directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file)
        print(f"Visualization saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Print full traceback for debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
