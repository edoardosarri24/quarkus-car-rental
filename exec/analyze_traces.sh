echo "extracting data from traces..."
cd E2E-analysis/analize_traces
kubectl cp analyzer:data/traces.json traces.json
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate car-rental
python main.py > statistics.txt
conda deactivate
rm -r __pycache__/
cd ../..