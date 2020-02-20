"""
This file contains the implementation of the three metrics required by the assignment. In particular, it defines:
- "compute_edit_distance_variability", which compute the edit distance variability of a given log using the
   Levenshtein distance formula
- "compute_variant_variability", which computes the number of variant (different traces) appearing in the input log
- "compute_my_variability", which computes the all-block entropy of an input log
"""
from math import log as logarithm
from typing import List

from progress.bar import Bar, IncrementalBar, ShadyBar

from log import Log, Trace, Event


def compute_edit_distance_variability(event_log: Log) -> float:
    """
    Computes the edit distance variability of the log using the Levenstein distance formula

    Args:
        event_log: an instance of Log class

    Returns:
        The computed edit distance of the input log
    """

    traces = event_log.trace_list

    distance: int = 0
    number_of_comparisons: int = 0

    bar = ShadyBar("Edit distance computation", max=len(traces) - 1)

    trace_1: Trace = traces[0]
    for trace_2 in traces:
        if trace_1 != trace_2:
            bar.next()
            distance += _levenshtein_distance(trace_1, trace_2) * trace_1.frequency * trace_2.frequency
            number_of_comparisons += 1
    bar.finish()

    return distance / number_of_comparisons


def _levenshtein_distance(t1: Trace, t2: Trace):
    """
    "Private" method used to compute the edit distance between two input traces using the Levenshtein algorithm.
    The Levenshtein distance is computed considering each event code of a trace as a different character.
    Args:
        t1 (Trace): the first input trace
        t2 (Trace): the second input trace

    Returns:
        the Levenshtein distance between the first and the second input trace
    """
    if t1.length > t2.length:
        t1, t2 = t2, t1

    distances = range(t1.length + 1)
    for i2, c2 in enumerate(t2.event_list):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(t1.event_list):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def compute_variant_variability(event_log: Log) -> int:
    """
    Computes the number of variants in the input Log
    Args:
        event_log (Log): the input log on which the metric is applied

    Returns:
        the number of variants in the input Log
    """
    return len(event_log.trace_list)


def compute_my_variability(event_log: Log) -> float:
    """
    Computes the prefix entropy of the input Log
    Args:
        event_log (Log): the input log

    Returns:
        the prefix-block entropy
    """
    prefixes: List[List[Event]] = []
    bar: Bar = IncrementalBar("Prefix generation", max=len(event_log.trace_list))
    for trace in event_log.trace_list:
        trace_prefixes: List[List[Event]] = trace.get_all_prefixes()

        for prefix in trace_prefixes:
            if prefix not in prefixes:
                prefixes.append(prefix)
        bar.next()
    bar.finish()

    entropy: float = 0

    bar = ShadyBar("Prefix likelihood estimation", max=len(prefixes))
    for prefix in prefixes:

        p: float = _prefix_likelihood_estimator(event_log, prefix)
        entropy += p * logarithm(p, 10)

        bar.next()
    bar.finish()

    entropy *= -1

    return entropy


def _prefix_likelihood_estimator(log: Log, prefix: List[Event]) -> float:
    """
    Computes the prefix likelihood estimate of a given prefix in a given log
    Args:
        log (Log): the log
        prefix (List[Event]): the prefix to search in log

    Returns:
        the prefix likelihood estimate of "prefix" in "log"
    """
    numerator: int = 0
    denominator: int = sum(trace.length for trace in log.trace_list)

    for trace in log.trace_list:
        if trace.contains_prefix(prefix):
            numerator += 1

    return numerator / denominator
