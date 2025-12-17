import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import traceback

def main():
    # Define file paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eulero_file = os.path.join(script_dir, '../input_file/eulero_CDF.csv')
    real_file = os.path.join(script_dir, '../input_file/real_e2e_execution_time.csv')
    output_file = os.path.join(script_dir, '../results/compare_e2e_distribution.pdf')

    # Check if files exist
    if not os.path.exists(eulero_file) or not os.path.exists(real_file):
        print(f"Error: Files not found.\nLooking for:\n{eulero_file}\n{real_file}")
        sys.exit(1)

    try:
        # Read the CSV files and check required columns
        df_eulero = pd.read_csv(eulero_file)
        df_real = pd.read_csv(real_file)
        if not {'time', 'cdf'}.issubset(df_eulero.columns):
            print(f"Error: '{eulero_file}' must contain 'time' and 'cdf' columns.")
            sys.exit(1)
        if 'duration_ms' not in df_real.columns:
            print(f"Error: '{real_file}' must contain 'duration_ms' column.")
            sys.exit(1)

        # eulero - PDF is the derivative of CDF: d(cdf) / d(time)
        dt_eulero = df_eulero['time'].diff()
        dcdf_eulero = df_eulero['cdf'].diff()
        pdf_eulero = dcdf_eulero / dt_eulero
        pdf_eulero = pdf_eulero.fillna(0)

        # real data
        real_times = df_real['duration_ms'].sort_values()
        n_real = len(real_times)
        cdf_real = np.arange(1, n_real + 1) / n_real

        # plottng CDF
        plt.figure(figsize=(14, 6))
        plt.subplot(1, 2, 1)
        plt.plot(real_times, cdf_real, label='Real CDF', color='red', linewidth=2)
        plt.plot(df_eulero['time'], df_eulero['cdf'], label='Eulero (Approx) CDF', color='blue', linewidth=2)
        plt.xlabel('Time (ms)')
        plt.ylabel('CDF')
        plt.title('Cumulative Distribution Function (CDF)')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # plottng PDF
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
    main()