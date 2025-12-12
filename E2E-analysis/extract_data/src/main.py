import json
import sys
import math
import csv
import os
import shutil
from collections import defaultdict
from distribution_fitting import fit_distribution

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

def analyze_all_traces(traces):
    e2e_durations = []
    filtered_out_count = 0
    
    # Structure: service_key -> segment_name -> list of durations
    granular_executions = defaultdict(lambda: defaultdict(list))
    
    # Structure: service_key -> list of total net durations (for total stats)
    total_executions = defaultdict(list)

    # Structure: "Source -> Target" -> list of overheads
    network_latencies = defaultdict(list)
    
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
        
        # FILTERING: Discard traces longer than 300ms
        if total_duration > 170:
            filtered_out_count += 1
            continue
            
        e2e_durations.append(total_duration)

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

    # Prepare Final Output
    output_data = {
        "trace_count": len(e2e_durations),
        "filtered_out_traces": filtered_out_count,
        "e2e_statistics": e2e_stats,
        "service_total_statistics": service_total_stats,
        "granular_segment_statistics": granular_stats,
        "network_latency_statistics": latency_stats
    }
    
    # Save to JSON
    json_file_path = os.path.join(output_dir, 'trace_analysis_stats.json')
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=2)
        print(f"Successfully saved JSON stats to {json_file_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving JSON: {e}", file=sys.stderr)
        
    # Print a preview to stdout
    print(json.dumps(output_data, indent=2))

if __name__ == "__main__":
    file_path = 'input_file/traces.json'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    traces = parse_traces(file_path)
    analyze_all_traces(traces)
    
    # Cleanup __pycache__ directory if it exists
    pycache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__pycache__")
    if os.path.exists(pycache_dir):
        try:
            shutil.rmtree(pycache_dir)
        except Exception as e:
            print(f"Error removing {pycache_dir}: {e}", file=sys.stderr)
    