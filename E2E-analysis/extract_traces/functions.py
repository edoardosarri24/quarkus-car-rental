import json
from collections import defaultdict
import numpy as np

"""
Given the JSON Lines file, extracts the traces and identifies the spans that belong to each one.
"""
def extract_traces(file_path):
    # The primary key is traceID. The value is a set of spans, unique according to their key.
    traces = defaultdict(dict)
    # begin the parsing of the JSON Lines file
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # each line is a JSON object
                data = json.loads(line)
                for resource_span in data.get("resourceSpans", []):
                    # extract service name
                    service_name = "unknown-service"
                    resource = resource_span.get("resource", {})
                    for attr in resource.get("attributes", []):
                        if attr.get("key") == "service.name":
                            service_name = attr.get("value", {}).get("stringValue", "unknown-service")
                    # define the spans for each trace.
                    for scope_span in resource_span.get("scopeSpans", []):
                        for span in scope_span.get("spans", []):
                            # add service name to span
                            span['serviceName'] = service_name
                            # Use spanId as key to handle duplicates
                            traces[span['traceId']][span['spanId']] = span
            except json.JSONDecodeError:
                pass # skip invalid lines
    return traces

"""
Filters the trace and maintain only those that are releted to the specific workflow.
"""
def filter_traces_for_workflow(traces):
    trace_lenght = 17
    target_trace_ids = set()
    for trace_id, spans_dict in traces.items():
        for _, span in spans_dict.items():
            if (span.get('serviceName') == 'users-service' and
                span.get('name') == 'POST /reserve' and
                len(spans_dict) == trace_lenght):
                    target_trace_ids.add(trace_id)
    filtered_traces = {trace_id: traces[trace_id] for trace_id in target_trace_ids}
    return filtered_traces

"""
print the spans of the filtered traces in a human-readable format.
"""
def print_traces(traces):
    for trace_id, spans_dict in traces.items():
        # Convert the dictionary of spans to a list for sorting
        spans = list(spans_dict.values())
        # Sort spans by start time
        spans.sort(key=lambda s: int(s['startTimeUnixNano']))

        print(f"--- Trace ID: {trace_id} ---")

        root_span = next((s for s in spans if 'parentSpanId' not in s), spans[0])
        trace_start_time = int(root_span['startTimeUnixNano'])

        for i, span in enumerate(spans):
            start_time = int(span['startTimeUnixNano'])
            end_time = int(span['endTimeUnixNano'])

            duration_ms = (end_time - start_time) / 10**6
            start_offset_ms = (start_time - trace_start_time) / 10**6

            service = span.get('serviceName', 'unknown-service')
            operation_name = span.get('name', 'unknown-operation')

            # Basic hierarchy indentation
            indent = ""
            if 'parentSpanId' in span:
                parent_found = any(s['spanId'] == span['parentSpanId'] for s in spans)
                if parent_found:
                    indent = "  "

            print(f"{i+1}.{indent} Service: {service:<25} | Operation: {operation_name:<40} | Duration: {duration_ms:.2f} ms | Start Offset: {start_offset_ms:.2f} ms")
        print("\n")

"""
collect statistics (i.e., exection time, mean, variance, standard deviation
and variation coefficient) for each operation across all traces.
"""
def collect_statisctics(traces):
    # extract durations for each <service,operation>
    operation_durations = defaultdict(list)
    for _, spans_dict in traces.items():
        spans = list(spans_dict.values())
        for span in spans:
            service_name = span.get('serviceName', 'unknown-service')
            operation_name = span.get('name', 'unknown-operation')
            start_time = int(span['startTimeUnixNano'])
            end_time = int(span['endTimeUnixNano'])
            duration = (end_time - start_time)
            key = (service_name, operation_name)
            operation_durations[key].append(duration)
    # compute statistics
    statistics = {}
    for serive_and_operation, durations in operation_durations.items():
        mean_duration = np.mean(durations)
        variance_duration = np.var(durations)
        std_dev_duration = np.std(durations)
        if mean_duration > 0:
            coeff_variation = std_dev_duration / mean_duration
        else:
            coeff_variation = 0
        statistics[serive_and_operation] = [
            durations,
            mean_duration,
            variance_duration,
            std_dev_duration,
            coeff_variation]
    return statistics

"""
print the collected statistics in a human-readable format.
"""
def print_statistics(statistics):
    print(f"{'Service':<25} | {'Operation':<40} | {'Mean (ms)':<12} | {'Variance':<12} | {'Std Dev':<12} | {'Coeff of Var':<12}")
    print("-" * 120)
    for (service_name, operation_name), stats in statistics.items():
        durations, mean_duration, variance_duration, std_dev_duration, coeff_variation = stats
        mean_ms = mean_duration / 10**6
        variance_ms = variance_duration / (10**6)**2
        std_dev_ms = std_dev_duration / 10**6
        print(f"{service_name:<25} | {operation_name:<40} | {mean_ms:<12.2f} | {variance_ms:<12.2f} | {std_dev_ms:<12.2f} | {coeff_variation:<12.4f}")