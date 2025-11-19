kubectl cp analyzer:data/traces.json E2E-analysis/extract_traces/traces.json
source /opt/miniconda3/etc/profile.d/conda.sh 
conda activate car-rental
python E2E-analysis/extract_traces/main.py > E2E-analysis/extract_traces/visual.txt
conda deactivate
rm -r E2E-analysis/extract_traces/__pycache__/