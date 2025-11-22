echo "extracting data from traces..."
cd E2E-analysis/data
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate car-rental
python main.py > distribution_statistics_traces.txt
conda deactivate
rm -r __pycache__/
cd ../..