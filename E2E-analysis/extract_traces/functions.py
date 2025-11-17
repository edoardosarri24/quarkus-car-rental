import json
from collections import defaultdict

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
                print(f"Warning! Could not decode JSON from line: {line.strip()}")
    return traces

"""
Filters the trace and maintain only those that are releted to the specific workflow.
"""
def filter_traces_for_workflow(traces):
    target_trace_ids = set()
    for trace_id, spans_dict in traces.items():
        for _, span in spans_dict.items():
            if span.get('serviceName') == 'users-service' and span.get('name') == 'POST /reserve':
                target_trace_ids.add(trace_id)
    filtered_traces = {trace_id: traces[trace_id] for trace_id in target_trace_ids}
    return filtered_traces

"""
print the spans of the filtered traces in a human-readable format.
"""
def print_traces(filtered_traces):
    for trace_id, spans_dict in filtered_traces.items():
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