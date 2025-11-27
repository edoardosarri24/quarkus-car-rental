import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def main():
    # Define file paths
    approx_file = 'approxCDF.csv'
    real_file = 'realCDF.csv'
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
        required_cols = {'time', 'cdf'}
        if not required_cols.issubset(df_approx.columns) or not required_cols.issubset(df_real.columns):
            print("Error: CSV files must contain 'time' and 'cdf' columns.")
            sys.exit(1)

        # Calculate PDF (Derivative of CDF)
        # PDF = diff(cdf) / diff(time)

        # Approx PDF
        dt_approx = df_approx['time'].diff()
        dcdf_approx = df_approx['cdf'].diff()
        pdf_approx = dcdf_approx / dt_approx

        # Real PDF
        dt_real = df_real['time'].diff()
        dcdf_real = df_real['cdf'].diff()
        pdf_real = dcdf_real / dt_real

        # Plotting
        plt.figure(figsize=(14, 6))

        # Plot CDF Comparison
        plt.subplot(1, 2, 1)
        plt.plot(df_real['time'], df_real['cdf'], label='Real CDF', color='blue')
        plt.plot(df_approx['time'], df_approx['cdf'], label='Approx CDF', color='red')
        plt.xlabel('Time')
        plt.ylabel('CDF')
        plt.title('Cumulative Distribution Function')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Plot PDF Comparison
        plt.subplot(1, 2, 2)
        plt.plot(df_real['time'], pdf_real, label='Real PDF', color='blue')
        plt.plot(df_approx['time'], pdf_approx, label='Approx PDF', color='red')
        plt.xlabel('Time')
        plt.ylabel('PDF')
        plt.title('Probability Density Function')
        plt.grid(True, alpha=0.3)
        plt.legend()

        plt.suptitle('E2E Distribution Function', fontsize=16)
        plt.tight_layout()

        # Save the plot
        plt.savefig(output_file)
        print(f"Visualization saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
