# -*- coding: utf-8 -*-
""" Michele Tagliabue (student id 1206966), Claudio Rimensi (student id 1207423)

This is an implementation of Project #1 of 2019/2020 Process Mining class.

Instruction:
    This application requires that you have installed Python. We have tested it on Python 3.7.6 on Windows 10 x64.
    Furthermore, you need to have installed the pm4py, matplotlib, progress and colorama libraries
    Finally, we recommend that you have added python to your PATH environmental variable.

    To run the application:
        1. Open a terminal inside the directory where main.py (this file) is located
        2. Run "pip3 install pm4py matplotlib progress colorama" to install all required dependencies
        3. Type "python main.py"
        4. Wait
"""
from colorama import init, Fore, Back, Style

import time
from typing import Dict, List, Tuple

import pm4py.objects.log.log as EventLog
from pm4py.objects.log.importer.xes import factory as xes_import_factory

from matplotlib import pyplot as plt

from log import Log, Event
from variability import compute_edit_distance_variability, compute_variant_variability, compute_my_variability


def load_file(path: str) -> EventLog:
    """
    Loads the input file and passes it to pm4py parser
    Args:
        path:

    Returns:

    """
    return xes_import_factory.apply(path)


def process_file(file_path: str) -> Tuple[int, float, float, float]:
    """
    Computes all the metrics of a given input file log
    Args:
        file_path (str): the input file path (relative or absolute)

    """
    start_time: float = time.clock()
    print(Fore.BLUE, "Log %s" % file_path, Fore.RESET)
    print("Step 1: Decoding log..\n")
    log_file = load_file(file_path)

    print("Step 2: Log processing...")
    log: Log = Log()
    log.load(log_file)

    trace_frequencies: Dict[int, int] = {}
    for trace in log.trace_list:
        if trace.frequency not in trace_frequencies.keys():
            trace_frequencies[trace.frequency] = 0
        trace_frequencies[trace.frequency] += 1

    trace_frequencies_string: str = ""
    for frequency in trace_frequencies:
        trace_frequencies_string += "- %d traces appears %d times\n" % (trace_frequencies[frequency], frequency)

    print("Total number of traces: %d" % log.size)
    print("Trace frequencies:\n%s" % trace_frequencies_string)

    print("Step 3: Metrics computation:", Fore.RESET)

    vv: int = compute_variant_variability(log)  # Variant variabilty
    pvv: float = vv * 100 / log.size
    print("3.1: Number of variants: %d" % vv)
    print("     Variability (perc.): %0.3f%%" % pvv)

    print("3.2: Edit distance:")
    ed: float = compute_edit_distance_variability(log)  # edit distance variability
    print("     value: %0.3f" % ed)
    print("3.3: Our metric:")
    om: float = compute_my_variability(log)  # Our metric
    print("    Prefix entropy: %f" % om, "\n")

    end_time: float = time.clock()
    final_time: float = (end_time - start_time)
    print(Fore.CYAN, "Elapsed time: %d seconds\n\n" % final_time, Fore.RESET)

    return vv, pvv, ed, om


def _print_event_list(event_list_list: List[List[Event]]) -> str:
    """
    Computes a string representation of the list of event list is
    Args:
        event_list_list (List[List[Event]]): the list of list of events to print

    Returns:
        the string representation of the input parameter
    """
    output_str: str = ""
    for event_list in event_list_list:
        output_str += "["
        sep: str = ""
        for event in event_list:
            output_str += sep + str(event.event_code)
            sep = ", "
        output_str += "], "

    return output_str


if __name__ == "__main__":
    init()  # Colorama initialization

    log_file_names: List[str] = ["BPIChallenge2011", "BPIChallenge2012", "BPIChallenge2017"]
    x: List[int] = list(range(len(log_file_names)))  # x-axis values

    variants: List[int] = []
    perc_variants: List[float] = []
    event_distances: List[float] = []
    our_metrics: List[float] = []

    for log_file_name in log_file_names:
        variant_variability, perc_variant, event_distance, our_metric = process_file("xes/%s.xes" % log_file_name)

        variants.append(variant_variability)
        perc_variants.append(perc_variant)
        event_distances.append(event_distance)
        our_metrics.append(our_metric)

    colors = ['C1', 'C2', 'C3']

    plt.bar(x, variants, color=colors)
    plt.title("Number of variants")
    plt.xticks(x, log_file_names)
    plt.savefig("plots/variants.png")
    plt.show()

    plt.title("Percentage of variability")
    plt.bar(x, perc_variants, color=colors)
    plt.xticks(x, log_file_names)
    # plt.ylim(100)
    plt.savefig("plots/perc_variants.png")
    plt.show()

    plt.title("Edit distance variability")
    plt.bar(x, event_distances, color=colors)
    plt.yscale("log")
    plt.xticks(x, log_file_names)
    plt.savefig("plots/edit_distance.png")
    plt.show()

    plt.title("Prefix entropy (our metric)")
    plt.bar(x, our_metrics, color=colors)
    plt.xticks(x, log_file_names)
    plt.savefig("plots/prefix_entropy.png")
    plt.show()
