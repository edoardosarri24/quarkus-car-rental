import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def main():
    # Define file paths
    input_file = 'approxCDF.csv'
    output_file = 'results/approx_distribution_plot.pdf'

    # Determine script directory to correctly locate the csv if run from project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, input_file)
    output_path = os.path.join(script_dir, output_file)

    # Ensure results directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: '{input_path}' does not exist.")
        sys.exit(1)

    print(f"Reading data from: {input_path}")

    try:
        # Read the CSV file
        df = pd.read_csv(input_path)

        # Check required columns
        required_cols = {'time', 'cdf'}
        if not required_cols.issubset(df.columns):
            print("Error: CSV file must contain 'time' and 'cdf' columns.")
            sys.exit(1)

        # Calculate PDF (Derivative of CDF)
        # PDF = diff(cdf) / diff(time)
        dt = df['time'].diff()
        dcdf = df['cdf'].diff()
        pdf = dcdf / dt

        # Fill NaN values (first element will be NaN due to diff)
        pdf = pdf.fillna(0)

        # Plotting
        plt.figure(figsize=(14, 6))

        # Plot CDF
        plt.subplot(1, 2, 1)
        plt.plot(df['time'], df['cdf'], label='Approx CDF', color='red')
        plt.xlabel('Time')
        plt.ylabel('CDF')
        plt.title('Cumulative Distribution Function')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Plot PDF
        plt.subplot(1, 2, 2)
        plt.plot(df['time'], pdf, label='Approx PDF', color='red')
        plt.xlabel('Time')
        plt.ylabel('PDF')
        plt.title('Probability Density Function')
        plt.grid(True, alpha=0.3)
        plt.legend()

        plt.suptitle('Approximate Distribution Analysis', fontsize=16)
        plt.tight_layout()

        # Save the plot
        plt.savefig(output_path)
        print(f"Visualization saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()