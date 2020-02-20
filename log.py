"""
This file contains the Event, Trace and Log classes used to encapsulate events, traces and logs to simplify the
computation of the metrics.
"""
from typing import List, Dict, Optional, Set
import pm4py.objects.log.log as EventLog


class Event:
    """
    Class that represents an event
    """

    def __init__(self, event_code: int, event_name: str):
        """
        Class constructor

        Args:
            event_code (int): the integer event code
            event_name (str): the event name
        """
        self.event_name: Optional[str] = event_name
        self.event_code: int = event_code

    @staticmethod
    def _is_valid_operand(other) -> bool:
        return (hasattr(other, "event_name") and
                hasattr(other, "event_code"))

    def __eq__(self, other) -> bool:
        """
        Equals operator override

        Args:
            other: the other object to compare

        Returns:
            True if current instance equals "object", False otherwise.
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.event_code == other.event_code and self.event_name == other.event_name

    def __str__(self) -> str:
        """
        String representation of an Event (mainly for debug purpose)
        Returns:
            the string-version of the event code
        """
        return str(self.event_code)


class Trace:
    """
    Class that represents a trace object, composed of:
    - The sorted list of events appearing, for example [a,b,b,c] to represent <a,b,b,c>
    - The frequency, namely the number of times the trace appears in the log. For example, in case of <a,b,b,c>^3,
      frequency is 3
    """

    def __init__(self, event_list: List[Event]):
        """
        Class constructor

        Args:
            event_list (List[Event]): the sorted event list of which the trace is composed
        """
        self.event_list: List[Event] = event_list
        self.frequency: int = 1

    @property
    def length(self) -> int:
        """
        Returns the length of the trace

        Returns:
            length of the trace
        """
        return len(self.event_list)

    def get_all_prefixes(self) -> List[List[Event]]:
        """
        Methods that computes all the prefixes of the current trace
        Returns:
            a list containing all the list of events that are prefixes of the current trace
        """
        prefixes: List[List[Event]] = []
        for i in range(self.length):
            sublist: List[Event] = self.event_list[0:i]
            prefixes.append(sublist)

        return prefixes

    def contains_prefix(self, prefix: List[Event]) -> bool:
        """
        Check if the current trace has the prefix passed as parameter
        Args:
            prefix (List[Event]): the prefix to check

        Returns:
            True if the current trace starts with the prefix passed as parameter
        """
        if len(prefix) > self.length:
            return False

        for i in range(len(prefix)):
            if prefix[i] != self.event_list[i]:
                return False

        return True

    @staticmethod
    def _is_valid_operand(other) -> bool:
        """
        Method used by the "==" operator. It checks if the object referenced by the parameter "other" has the same
        attributes of a Trace instance (event_list and frequency)

        Args:
            other: the object used for the comparison

        Returns:
            True if "other" has the same structure of a Trace instance
        """
        return (hasattr(other, "event_list") and
                hasattr(other, "frequency"))

    def __eq__(self, other):
        """
        Overload of "==" operator to make the comparison between two Trace instance possible.
        For optimization porpoise, two traces are equal if their event list contain the same sequence of events
        (the frequency is ignored).

        Args:
            other (Trace): the other Trace object to compare.

        Returns:
            True if the objects are equivalent, False otherwise.
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.event_list == other.event_list

    def __str__(self):
        """
        String representation of a Trace object.
        Returns:
            a string representing the Trace object
        """
        string_representation: str = ""
        sep: str = ""
        for event in self.event_list:
            string_representation += sep + "%d" % event.event_code
            sep = ", "

        return string_representation


class Log:
    """
    Class that represent a whole log. It is composed by:
    - A dictionary that maps the string representation of an event (for example "1e consult poliklinisch") onto a unique
      integer value, which will be the code of the event
    - A list of traces, which corresponds to the "corpus" of the log.
    """

    def __init__(self):
        """
        Constructor. No parameter needed.
        """
        self.dictionary: Dict[str, int] = {}
        self.trace_list: List[Trace] = []

    def get_keys_list(self) -> List[str]:
        """
        Returns the list of all the keys (so the string representations) of all events encountered so far.
        Returns:
            the list of all the keys (so the string representations) of all events encountered so far
        """
        return list(self.dictionary.keys())

    def get_event(self, event_name: str) -> Event:
        """
        Returns the Event class instance corresponding to the given event name.
        Args:
            event_name (str): the name of the event

        Returns:
            an Event instance
        """
        event_code: int = self.get_keys_list().index(event_name)
        return Event(event_code, event_name)

    def get_trace(self, event_list: List[Event]) -> Optional[Trace]:
        """
        Returns a Trace instance with an event list equivalent to "event_list" if already encountered. Otherwise None is
        returned.
        Args:
            event_list (List[Event]: a list of event

        Returns:
            The corresponding trace, or None if it has not already been encountered.
        """
        for trace in self.trace_list:
            if trace.event_list == event_list:
                return trace
        return None

    @property
    def size(self) -> int:
        """
        Property that defines the size of the Log. We have defined the property as the total number of traces (including
        repetitions) that the Log contains.

        Returns:
            the log size
        """
        total_size: int = 0

        for trace in self.trace_list:
            total_size += trace.frequency

        return total_size

    def load(self, input_log: EventLog):
        """
        Read and parse the log file given as argument
        Args:
            input_log: (EventLog) the pm4py EventLog instance to parse
        """
        for case_index, case in enumerate(input_log):
            events_list: List[Event] = []

            for event_index, event in enumerate(case):
                key_name: str = event["concept:name"]

                if key_name not in self.dictionary.keys():
                    self.dictionary[key_name] = 0

                self.dictionary[key_name] += 1

                events_list.append(self.get_event(key_name))
            saved_trace: Trace = self.get_trace(events_list)
            if saved_trace is None:
                self.trace_list.append(Trace(events_list))
            else:
                saved_trace.frequency += 1
