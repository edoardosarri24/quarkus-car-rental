import os
import json
import numpy as np
import math
from collections import defaultdict
from distribution_fitting import *

def extract_traces(file_path):
    """
    Given the JSON Lines file, extracts the traces and identifies the spans that belong to each one.
    """
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

def filter_traces_for_workflow(traces):
    """
    Filters the trace and maintain only those that are releted to the specific workflow.
    """
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

def sum_exec_time_same_consecutive_service(traces):
    """
    sum the time of the same consecutive service in one operation
    """
    processed_traces = {}
    for trace_id, spans_dict in traces.items():
        if not spans_dict:
            continue
        spans = sorted(list(spans_dict.values()), key=lambda s: int(s['startTimeUnixNano']))
        if not spans:
            processed_traces[trace_id] = {}
            continue
        merged_spans_list = []
        # Start with the first span
        current_merged_span = spans[0].copy()
        for i in range(1, len(spans)):
            next_span = spans[i]
            if next_span.get('serviceName') == current_merged_span.get('serviceName'):
                # Same service, merge it
                duration_current = int(current_merged_span['endTimeUnixNano']) - int(current_merged_span['startTimeUnixNano'])
                duration_next = int(next_span['endTimeUnixNano']) - int(next_span['startTimeUnixNano'])
                # Update endTimeUnixNano to reflect summed duration
                current_merged_span['endTimeUnixNano'] = str(int(current_merged_span['startTimeUnixNano']) + duration_current + duration_next)
            else:
                # Different service, so the current merged span is complete
                merged_spans_list.append(current_merged_span)
                # Start a new merged span
                current_merged_span = next_span.copy()
        # Add the very last merged span
        merged_spans_list.append(current_merged_span)
        # Convert list back to dictionary using the spanId of the first span in each merged group
        new_spans_dict = {span['spanId']: span for span in merged_spans_list}
        processed_traces[trace_id] = new_spans_dict
    return processed_traces

def print_traces(traces):
    """
    print the spans of the filtered traces in a human-readable format.
    """
    for trace_id, spans_dict in traces.items():
        # Convert the dictionary of spans to a list for sorting
        spans = list(spans_dict.values())
        # Sort spans by start time
        spans.sort(key=lambda s: int(s['startTimeUnixNano']))
        print(f"--- Trace ID: {trace_id} ---")
        for i, span in enumerate(spans):
            start_time = int(span['startTimeUnixNano'])
            end_time = int(span['endTimeUnixNano'])
            duration_ms = (end_time - start_time) / 10**6
            service = span.get('serviceName', 'unknown-service')
            operation_name = span.get('name', 'unknown-operation')
            # Basic hierarchy indentation
            print(f"#{i+1:<2} | Service: {service:<25} | Operation: {operation_name:<30} | Duration: {duration_ms:.2f} ms")
        print("\n")
    print("\n\n")

def collect_statisctics(traces):
    """
    collect statistics (i.e., exection time, mean, variance, standard deviation
    and variation coefficient) for each operation across all traces.
    """
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
    for service_and_operation, durations in operation_durations.items():
        max_duration = max(durations)
        min_duration = min(durations)
        mean_duration = np.mean(durations)
        variance_duration = np.var(durations)
        std_dev_duration = np.std(durations)
        if mean_duration > 0:
            coeff_variation = std_dev_duration / mean_duration
        else:
            coeff_variation = 0
        statistics[service_and_operation] = [
            duration,
            min_duration,
            max_duration,
            mean_duration,
            variance_duration,
            std_dev_duration,
            coeff_variation]
    return statistics

def print_statistics(statistics):
    """
    print the collected statistics in a human-readable format.
    """
    print(f"{'Service':<25} | {'Operation':<28} | {'Min (ms)':<8} | {'Max (ms)':<8} | {'Mean (ms)':<10} | {'Variance':<8} | {'Std Dev':<8} | {'CV':<8}")
    print("-" * 130)
    for (service_name, operation_name), stats in statistics.items():
        _, min_duration, max_duration, mean_duration, variance_duration, std_dev_duration, coeff_variation = stats
        min_ms = min_duration / 10**6
        max_ms = max_duration / 10**6
        mean_ms = mean_duration / 10**6
        variance = variance_duration / (10**6)**2
        std_dev = std_dev_duration / 10**6
        print(f"{service_name:<25} | {operation_name:<28} | {min_ms:<8.3f} | {max_ms:<8.3f} | {mean_ms:<10.3f} | {variance:<8.3f} | {std_dev:<8.3f} | {coeff_variation:<8.3f}")
    print("\n\n")

def distribution_fitting(statistics):
    distributions = {}
    for service_and_operation, statistic in statistics.items():
        if statistic[6] > 1:
            lambdas = fit_hyper_exponential(statistic[3]/(10**6), statistic[6])
            distributions[service_and_operation] = ("hyperExp",) + lambdas
        elif statistic[6] < 1 and statistic[6] > (1/math.sqrt(2)):
            lambdas = fit_hypo_exponential(statistic[3]/(10**6), statistic[6])
            distributions[service_and_operation] = ("hypoExp",) + lambdas
        else:
            raise ValueError(f"Coefficient of variation {statistic[6]} for {service_and_operation} is not in a supported range for distribution fitting.")
    return distributions

def print_distributions(distributions):
    """
    print the collected distributions in a human-readable format.
    """
    print(f"{'Service':<25} | {'Operation':<28} | {'distribution':<15} | {'p1':<10} | {'Lambda 1':<20} | {'p2':<10} | {'Lambda 2':<20}")
    print("-" * 140)
    for (service_name, operation_name), lambdas in distributions.items():
        if len(lambdas) == 3:
            distribution, lambda1, lambda2 = lambdas
            print(f"{service_name:<25} | {operation_name:<28} | {distribution:<15} | {'N/A':<10} | {lambda1:<20.4f} | {'N/A':<10} | {lambda2:<20.4f}")
        elif len(lambdas) == 5:
            distribution, p1, lambda1, p2, lambda2 = lambdas
            print(f"{service_name:<25} | {operation_name:<28} | {distribution:<15} | {p1:<10.4f} | {lambda1:<20.4f} | {p2:<10.4f} | {lambda2:<20.4f}")
    print("\n\n")

def collect_end_to_end_statistics(traces):
    """
    Collect end-to-end statistics for the workflow starting with users-service/reserve.
    The duration is calculated from the start of users-service/reserve to its end.
    """
    durations = []
    for trace_id, spans_dict in traces.items():
        for _, span in spans_dict.items():
            if span.get('serviceName') == 'users-service' and span.get('name') == 'POST /reserve':
                start_time = int(span['startTimeUnixNano'])
                end_time = int(span['endTimeUnixNano'])
                duration = end_time - start_time
                durations.append(duration)
                break
    if not durations:
        return {}
    max_duration = max(durations)
    min_duration = min(durations)
    mean_duration = np.mean(durations)
    variance_duration = np.var(durations)
    std_dev_duration = np.std(durations)
    if mean_duration > 0:
        coeff_variation = std_dev_duration / mean_duration
    else:
        coeff_variation = 0
    
    distribution_params = None
    if mean_duration > 0:
        mean_ms = mean_duration / 10**6
        if coeff_variation > 1:
            params = fit_hyper_exponential(mean_ms, coeff_variation)
            distribution_params = ("hyperExp",) + params
        elif coeff_variation < 1 and coeff_variation > (1/math.sqrt(2)):
            params = fit_hypo_exponential(mean_ms, coeff_variation)
            distribution_params = ("hypoExp",) + params

    return {
        "min": min_duration,
        "max": max_duration,
        "mean": mean_duration,
        "variance": variance_duration,
        "std_dev": std_dev_duration,
        "coeff_variation": coeff_variation,
        "distribution_params": distribution_params
    }

def print_end_to_end_statistics(stats):
    """
    Print the collected end-to-end statistics in a human-readable format.
    """
    if not stats:
        print("No end-to-end statistics available.")
        return
    print(f"{'Metric':<20} | {'Value'}")
    print("-" * 40)
    min_ms = stats['min'] / 10**6
    max_ms = stats['max'] / 10**6
    mean_ms = stats['mean'] / 10**6
    variance = stats['variance'] / (10**6)**2
    std_dev = stats['std_dev'] / 10**6
    cv = stats['coeff_variation']
    print(f"{'Min (ms)':<20} | {min_ms:.3f}")
    print(f"{'Max (ms)':<20} | {max_ms:.3f}")
    print(f"{'Mean (ms)':<20} | {mean_ms:.3f}")
    print(f"{'Variance':<20} | {variance:.3f}")
    print(f"{'Std Dev':<20} | {std_dev:.3f}")
    print(f"{'CV':<20} | {cv:.3f}")
    
    if stats.get('distribution_params'):
        params = stats['distribution_params']
        dist_type = params[0]
        print("-" * 40)
        print(f"{'Distribution':<20} | {dist_type}")
        if dist_type == "hyperExp":
            # params: ("hyperExp", p1, lambda1, p2, lambda2)
            p1, lambda1, p2, lambda2 = params[1:]
            print(f"{'p1':<20} | {p1:.4f}")
            print(f"{'Lambda 1':<20} | {lambda1:.4f}")
            print(f"{'p2':<20} | {p2:.4f}")
            print(f"{'Lambda 2':<20} | {lambda2:.4f}")
        elif dist_type == "hypoExp":
            # params: ("hypoExp", lambda1, lambda2)
            lambda1, lambda2 = params[1:]
            print(f"{'Lambda 1':<20} | {lambda1:.4f}")
            print(f"{'Lambda 2':<20} | {lambda2:.4f}")

    print("\n\n")

if __name__ == "__main__":
    #setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    traces_file = os.path.join(script_dir, "traces.json")
    # execution
    traces = extract_traces(traces_file)
    filtered_traces = filter_traces_for_workflow(traces)
    processed_traces = sum_exec_time_same_consecutive_service(filtered_traces)
    statistics = collect_statisctics(processed_traces)
    distributions = distribution_fitting(statistics)
    e2e_stats = collect_end_to_end_statistics(filtered_traces)
    print("E2E STATISTICS")
    print_end_to_end_statistics(e2e_stats)
    print("DISTRIBUTIONS")
    print_distributions(distributions)
    print("STATISTICS")
    print_statistics(statistics)
    print("PROCESSED TRACES")
    print_traces(processed_traces)