import json
import sys
import math
import csv
import os
import shutil
import random
from collections import defaultdict
from distribution_fitting import fit_distribution
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def parse_traces(file_path):
    traces = defaultdict(list)
    with open(file_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if 'resourceSpans' not in data:
                continue
            for rs in data['resourceSpans']:
                service_name = "unknown"
                if 'resource' in rs and 'attributes' in rs['resource']:
                    for attr in rs['resource']['attributes']:
                        if attr['key'] == 'service.name':
                            service_name = attr['value'].get('stringValue', 'unknown')
                            break
                if 'scopeSpans' in rs:
                    for ss in rs['scopeSpans']:
                        if 'spans' in ss:
                            for span in ss['spans']:
                                span['service_name'] = service_name
                                traces[span['traceId']].append(span)
    return traces

def is_db_call(span):
    if 'attributes' in span:
        for attr in span['attributes']:
            if attr['key'] == 'db.system':
                return True
    return False

def extract_execution_segments(span, all_spans_by_parent):
    """
    Breaks down the service execution into granular segments.
    Returns a list of dicts: {'name': 'Segment Name', 'duration': ms}
    """
    start_time = int(span['startTimeUnixNano'])
    end_time = int(span['endTimeUnixNano'])
    all_children = all_spans_by_parent.get(span['spanId'], [])
    # We only break flow on EXTERNAL calls. DB calls are part of the processing.
    # We identify external calls by EXCLUDING DB calls.
    external_calls = [child for child in all_children if not is_db_call(child)]
    external_calls.sort(key=lambda x: int(x['startTimeUnixNano']))
    segments = []
    current_cursor = start_time
    # Iterate through external calls to define segments before/between them
    for call in external_calls:
        call_start = int(call['startTimeUnixNano'])
        call_end = int(call['endTimeUnixNano'])
        # Calculate processing time before this call
        duration_ns = call_start - current_cursor
        # We only record significant segments (> 0.01ms to avoid noise from overlaps)
        if duration_ns > 10000:
            called_service = call.get('service_name', 'unknown')
            called_op = call.get('name', 'unknown')
            segment_name = f"Processing before calling {called_service} [{called_op}]"
            segments.append({
                "name": segment_name,
                "duration": duration_ns / 1e6
            })
            # Update cursor to the start of the call (we skip the call duration itself)
            current_cursor = call_end
        else:
            # If overlap or immediate call, just push cursor forward
            current_cursor = max(current_cursor, call_end)
    # Calculate final processing segment after the last call
    final_duration_ns = end_time - current_cursor
    if final_duration_ns > 10000:
        segments.append({
            "name": "Final Processing / Response Preparation",
            "duration": final_duration_ns / 1e6
        })
    # Edge case: No external calls? The whole span is one segment.
    if not external_calls and not segments:
        segments.append({
            "name": "Full Internal Execution",
            "duration": (end_time - start_time) / 1e6
        })
    return segments

def calculate_stats(data):
    n = len(data)
    if n == 0:
        return None
    mean_val = sum(data) / n
    min_val = min(data)
    max_val = max(data)
    if n > 1:
        variance_val = sum((x - mean_val) ** 2 for x in data) / (n - 1)
        std_dev_val = math.sqrt(variance_val)
    else:
        variance_val = 0.0
        std_dev_val = 0.0
    cv_val = (std_dev_val / mean_val) if mean_val != 0 else 0.0
    return {
        "mean": mean_val,
        "min": min_val,
        "max": max_val,
        "variance": variance_val,
        "std_dev": std_dev_val,
        "cv": cv_val
    }

def calculate_latency_stats(data):
    """
    Simplified stats calculation for network latency (only mean and variance).
    """
    n = len(data)
    if n == 0:
        return None
    mean_val = sum(data) / n
    if n > 1:
        variance_val = sum((x - mean_val) ** 2 for x in data) / (n - 1)
    else:
        variance_val = 0.0
    return {
        "mean": mean_val,
        "variance": variance_val
    }

def correlation_matrices(traces_groups, output_dir):
    for group_name in traces_groups.keys():
        input_csv_name = f"correlation_input_{group_name}.csv"
        input_csv_path = os.path.join(output_dir, input_csv_name)
        output_pdf_name = f"correlation_matrix_{group_name}.pdf"
        output_pdf_path = os.path.join(output_dir, output_pdf_name)
        if os.path.exists(input_csv_path):
            try:
                df = pd.read_csv(input_csv_path)
                if not df.empty and df.shape[1] > 1:
                    # Calculate Pearson correlation
                    corr_matrix = df.corr(method='pearson')
                    # Create Mappings for Short IDs
                    full_names = corr_matrix.columns.tolist()
                    id_map = {name: f"S{i+1}" for i, name in enumerate(full_names)}
                    short_names = [id_map[name] for name in full_names]
                    # Create PDF
                    with PdfPages(output_pdf_path) as pdf:
                        num_vars = len(full_names)
                        # Heuristic size: base size + scaling factor
                        fig_size = max(8, num_vars * 0.8)
                        fig, ax = plt.subplots(figsize=(fig_size + 4, fig_size)) # Extra width for legend
                        # Plot Heatmap
                        cax = ax.imshow(corr_matrix.values, interpolation='nearest', cmap='coolwarm', vmin=-1, vmax=1)
                        # Add Colorbar
                        cbar = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
                        cbar.set_label('Correlation Coefficient')
                        # Set Ticks and Labels (Short IDs)
                        ax.set_xticks(range(num_vars))
                        ax.set_yticks(range(num_vars))
                        ax.set_xticklabels(short_names, rotation=45, ha="right")
                        ax.set_yticklabels(short_names)
                        # Add Cell Annotations
                        for i in range(num_vars):
                            for j in range(num_vars):
                                val = corr_matrix.iloc[i, j]
                                text_color = "white" if abs(val) > 0.5 else "black"
                                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=8)
                        plt.title(f"Correlation Matrix Heatmap: {group_name}", fontsize=14, pad=20)
                        # Create Legend text
                        legend_text = "\n".join([f"{v}: {k}" for k, v in id_map.items()])
                        # Place Legend to the right
                        plt.subplots_adjust(right=0.7) # Make room for legend
                        fig.text(0.75, 0.5, f"Legend:\n\n{legend_text}", fontsize=10, va='center', ha='left', bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black", alpha=0.8))
                        pdf.savefig(fig, bbox_inches='tight')
                        plt.close(fig)
                    print(f"Successfully saved correlation heatmap PDF to {output_pdf_path}", file=sys.stderr)
                else:
                    print(f"Skipping correlation PDF for {group_name}: Not enough data/columns.", file=sys.stderr)
            except Exception as e:
                print(f"Error calculating correlation PDF for {group_name}: {e}", file=sys.stderr)

def delete_correlationCSV(traces_groups, output_dir):
    for group_name in traces_groups.keys():
        csv_file_path = os.path.join(output_dir, f"correlation_input_{group_name}.csv")
        if os.path.exists(csv_file_path):
            try:
                os.remove(csv_file_path)
                print(f"Deleted temporary file: {csv_file_path}", file=sys.stderr)
            except Exception as e:
                print(f"Error deleting {csv_file_path}: {e}", file=sys.stderr)

def analyze_all_traces(traces, filter_value):
    # init
    e2e_durations = []
    filtered_out_count = 0
    # Structure: service_key -> segment_name -> list of durations
    granular_executions = defaultdict(lambda: defaultdict(list))
    # Structure: service_key -> list of total net durations (for total stats)
    total_executions = defaultdict(list)
    # Structure: "Source -> Target" -> list of overheads
    network_latencies = defaultdict(list)

    # For CSV Correlation: Store per-trace granular data
    # List of dicts: each dict is { "ColumnName": duration_sum } for a single trace
    all_trace_maps = []
    all_possible_columns = set()

    for trace_id, raw_spans in traces.items():
        spans_by_id = {span['spanId']: span for span in raw_spans}
        spans = list(spans_by_id.values())

        spans_by_parent = defaultdict(list)
        for span in spans:
            parent_id = span.get('parentSpanId')
            if parent_id:
                spans_by_parent[parent_id].append(span)

        root_span = None
        for span in spans:
            if (span.get('service_name') == 'users-service' and 
                span.get('name') == 'POST /reserve' and 
                span.get('kind') == 2):
                root_span = span
                break

        if not root_span:
            continue

        # 1. E2E Duration Check
        total_duration = (int(root_span['endTimeUnixNano']) - int(root_span['startTimeUnixNano'])) / 1e6

        if total_duration > filter_value:
            filtered_out_count += 1
            continue

        e2e_durations.append(total_duration)

        # Per-trace storage for correlation CSV
        trace_segment_map = {}

        # 2. Granular Segments for all participating services
        server_spans = [s for s in spans if s.get('kind') == 2]

        for span in server_spans:
            service = span.get('service_name', 'unknown')
            operation = span.get('name', 'unknown')
            service_key = f"{service} [{operation}]"

            # Get segments
            segments = extract_execution_segments(span, spans_by_parent)

            # Record segment stats
            total_net_time = 0
            for seg in segments:
                granular_executions[service_key][seg['name']].append(seg['duration'])
                total_net_time += seg['duration']

                # For CSV: Accumulate duration for this specific column in this trace
                # We sum in case of loops/multiple calls to same service-segment in one trace
                col_name = f"{service_key} - {seg['name']}"
                trace_segment_map[col_name] = trace_segment_map.get(col_name, 0.0) + seg['duration']
                all_possible_columns.add(col_name)

            # Record total stats
            total_executions[service_key].append(total_net_time)

            # 3. Network Latency Calculation
            parent_id = span.get('parentSpanId')
            if parent_id and parent_id in spans_by_id:
                client_span = spans_by_id[parent_id]

                # Only consider calls from other services (Kind=3 -> Kind=2 usually)
                if client_span.get('kind') == 3: # Client
                    client_duration = (int(client_span['endTimeUnixNano']) - int(client_span['startTimeUnixNano'])) / 1e6
                    server_duration = (int(span['endTimeUnixNano']) - int(span['startTimeUnixNano'])) / 1e6

                    overhead = client_duration - server_duration
                    if overhead < 0: overhead = 0

                    source = client_span.get('service_name', 'unknown')
                    target = span.get('service_name', 'unknown')
                    latency_key = f"{source} -> {target}"

                    network_latencies[latency_key].append(overhead)

        # Store the map for this trace
        all_trace_maps.append(trace_segment_map)

    # Save E2E durations to CSV
    output_dir = 'results'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_file_path = os.path.join(output_dir, 'real_e2e_execution_time.csv')
    try:
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['duration_ms'])
            for duration in e2e_durations:
                writer.writerow([duration])
        print(f"Successfully saved CSV to {csv_file_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving CSV: {e}", file=sys.stderr)

    # Save Granular Execution Segments to CSV (correlation_input)
    # SPLIT by execution path: First Choice, Second Choice, Third Choice

    traces_groups = {
        'first_choice': [],
        'second_choice': [],
        'third_choice': []
    }

    for t_map in all_trace_maps:
        # Check which path this trace belongs to based on keys
        # We look for the distinguishing service name in the keys
        keys_str = "".join(t_map.keys())

        if 'first-choice-service' in keys_str:
            traces_groups['first_choice'].append(t_map)
        elif 'second-choice-service' in keys_str:
            traces_groups['second_choice'].append(t_map)
        elif 'third-choice-service' in keys_str:
            traces_groups['third_choice'].append(t_map)
        else:
            # Trace doesn't match any known path (or maybe failed before reaching choice)
            pass

    for group_name, group_traces in traces_groups.items():
        if not group_traces:
            print(f"No traces found for group: {group_name}", file=sys.stderr)
            continue

        csv_file_name = f"correlation_input_{group_name}.csv"
        csv_file_path = os.path.join(output_dir, csv_file_name)

        try:
            # Collect all possible columns for THIS group
            group_columns = set()
            for t_map in group_traces:
                group_columns.update(t_map.keys())

            sorted_col_names = sorted(list(group_columns))

            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(sorted_col_names)

                for t_map in group_traces:
                    row = []
                    for col in sorted_col_names:
                        # Fill with empty string if column is missing in this specific trace
                        # (though ideally they should be structurally identical within a group)
                        row.append(t_map.get(col, ''))
                    writer.writerow(row)

            print(f"Successfully saved {group_name} CSV to {csv_file_path} ({len(group_traces)} traces)", file=sys.stderr)
        except Exception as e:
            print(f"Error saving {group_name} CSV: {e}", file=sys.stderr)

    # Calculate Statistics
    e2e_stats = calculate_stats(e2e_durations)

    # Calculate stats for TOTALs
    service_total_stats = {}
    for key, times in total_executions.items():
        stats = calculate_stats(times)
        if stats and stats['mean'] > 0 and stats['cv'] > 0:
            try:
                dist = fit_distribution(stats['mean'], stats['cv'])
                stats['distribution'] = dist
            except Exception:
                pass
        service_total_stats[key] = stats

    # Calculate stats for SEGMENTS
    granular_stats = {}
    for service_key, segments_dict in granular_executions.items():
        granular_stats[service_key] = {}
        for seg_name, times in segments_dict.items():
            stats = calculate_stats(times)
            if stats and stats['mean'] > 0 and stats['cv'] > 0:
                try:
                    dist = fit_distribution(stats['mean'], stats['cv'])
                    stats['distribution'] = dist
                except Exception:
                    pass
            granular_stats[service_key][seg_name] = stats

    # Calculate stats for LATENCY (Mean & Variance only)
    latency_stats = {}
    for key, times in network_latencies.items():
        latency_stats[key] = calculate_latency_stats(times)

    # correlation matrix
    correlation_matrices(traces_groups, output_dir)

    # Save to JSON
    output_data = {
        "trace_count": len(e2e_durations),
        "filtered_out_traces": filtered_out_count,
        "e2e_statistics": e2e_stats,
        "service_total_statistics": service_total_stats,
        "granular_segment_statistics": granular_stats,
        "network_latency_statistics": latency_stats
    }
    json_file_path = os.path.join(output_dir, 'trace_analysis_stats.json')
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=2)
        print(f"Successfully saved JSON stats to {json_file_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving JSON: {e}", file=sys.stderr)

    # Clean up correlation CSV files
    delete_correlationCSV(traces_groups, output_dir)

def cleanup():
    pycache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__pycache__")
    if os.path.exists(pycache_dir):
        try:
            shutil.rmtree(pycache_dir)
        except Exception as e:
            print(f"Error removing {pycache_dir}: {e}", file=sys.stderr)

if __name__ == "__main__":
    file_path = 'input_file/traces.json'
    filter_value = 1000
    percentage = 1

    traces = parse_traces(file_path)
    if percentage < 1.0:
        all_trace_ids = list(traces.keys())
        num_to_keep = int(len(all_trace_ids) * percentage)
        kept_trace_ids = set(random.sample(all_trace_ids, num_to_keep))
        traces = {k: v for k, v in traces.items() if k in kept_trace_ids}
        print(f"Randomly filtered traces. Keeping {len(traces)} traces ({percentage*100:.1f}% of {len(all_trace_ids)}).", file=sys.stderr)
    analyze_all_traces(traces, filter_value)
    cleanup()