from functions import *
import os

if __name__ == "__main__":
    #setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    traces_file = os.path.join(script_dir, "traces.json")
    # execution
    traces = extract_traces(traces_file)
    filtered_traces = filter_traces_for_workflow(traces)
    print_traces(filtered_traces)
    statistics = collect_statisctics(filtered_traces)
    print_statistics(statistics)