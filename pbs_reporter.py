#!/usr/bin/env python
"""
Collect results from a collection of PBS-job stdout files and outputs a CSV file of results.

  usage: ./pbs_reporter.py job_stdout_file [...]
  help:  ./pbs_reporter.py --help
"""

import os
import sys
import re
import argparse

def convert_to_iso8601(timestamp):
    """
    Ensure timestamps have a consistent, well known format
    """
    return re.sub(r'\s', 'T', timestamp)  # convert to ISO8601

def pbs_time_to_seconds(pbs_duration):
    """
    Convert hhh:mm:ss to seconds
    """
    fields = pbs_duration.split(':')
    return int(fields[0])*60*60 + int(fields[1])*60 + int(fields[2])

class PbsReportParser(object):
    """
    Parses a PBS stdout file. Extracted values become instance properties
    """
    _PATTERN = (   # pattern used by parser to match PBS standard output
        r"(?i)"
        r"^\s+Resource Usage on (?P<timestamp>\d{4}-\d\d-\d\d"
        r" \d\d:\d\d:\d\d)(\.\d+)?:$"
        r"\s+Job\s*Id:\s*(?P<job_id>\S+)\s*$"
        r"\s+Project:\s*(?P<project>\S+)\s*$"
        r"\s+Exit Status:\s*(?P<exit_status>\d+)(\s+\(Linux Signal (?P<signal>\d+)\))?$"
        r"\s+Service Units:\s*(?P<service_units>\S+)$"
        r"\s+NCPUs Requested:\s*(?P<ncpus_requested>\d+)"
        r"\s+NCPUs Used:\s*(?P<ncpus_used>\d+)\s*$"
        r"\s+CPU Time Used:\s*(?P<cpu_used>\d+:\d\d:\d\d)\s*$"
        r"\s+Memory Requested:\s*(?P<memory_requested>\S+)"
        r"\s+Memory Used:\s*(?P<memory_used>\S+)\s*$"
        r"(\s+Vmem Used:\s*(?P<vmem_used>\S+)$)?"
        r"\s+Walltime requested:\s*(?P<walltime_requested>\d+:\d\d:\d\d)"
        r"\s+Walltime Used:\s*(?P<walltime_used>\d+:\d\d:\d\d)\s*$"
        r"\s+JobFS request(ed)?:\s+(?P<jobfs_requested>\S+)"
        r"\s+JobFS used:\s*(?P<jobfs_used>\S+)\s*$"
        )

    pbs_pattern = re.compile(_PATTERN, re.MULTILINE) #pylint: disable=no-member

    @staticmethod
    def fields_available():
        """
        Return fields available from this Parser
        """
        pat = re.compile(r"<(?P<name>\S+?)>")
        found = pat.findall(PbsReportParser._PATTERN)
        if found is not None:
            return ",".join(found)+",path"+",stdout_size"+",cpu_utilisation" \
                +", walltime_requested_secs"+",walltime_used_secs"
        return ""

    def __init__(self, o_file_path):
        self.path = o_file_path
        self._parsefile(o_file_path, self.pbs_pattern)
        self._add_derived_properties()

    def _add_derived_properties(self):

        self.stdout_size = os.path.getsize(self.path)
        self.timestamp = convert_to_iso8601(self.timestamp)
        #pylint: disable=no-member
        self.walltime_requested_secs = pbs_time_to_seconds(self.walltime_requested)
        self.walltime_used_secs = pbs_time_to_seconds(self.walltime_used)
        self.cpu_used_secs = pbs_time_to_seconds(self.cpu_used)
        self.cpu_utilisation = round(pbs_time_to_seconds(self.cpu_used) * 100 \
            / (int(self.ncpus_used) * pbs_time_to_seconds(self.walltime_used)), 2)

    def _parsefile(self, o_file_path, pattern):
        """
        parse the content for the supplied file with the supplied pattern
        the named groups in the pattern become attributes of self
        """

        with open(o_file_path, 'r') as infile:
            content = infile.read()

        match = pattern.search(content)
        if match is None:
            raise ValueError("could not parse %s" % (o_file_path))
        else:
            self.__dict__.update(match.groupdict())

    def get_values(self, keys, none_value='?'):
        """
        return a list of values for the supplied list of keys
        """
        dickt = self.__dict__
        return [str(dickt[k]) if k in dickt else none_value for k in keys]

def main():
    """
    mainline
    """
    # parser the arguments

    default_keys = PbsReportParser.fields_available()
    parser = argparse.ArgumentParser(description='Collect and output PBS job statistics')
    parser.add_argument('-k', '--keys', help='comma separated list of keys', default=default_keys)
    parser.add_argument('--keys_only', help='print the keys to be output', action='store_true')
    parser.add_argument('--no_keys', help='supress the output of keys', action='store_true')
    parser.add_argument('paths', nargs='*', help='paths to PBS output files')
    parser.set_defaults(no_keys=False, keys_only=False)
    args = parser.parse_args()

    # print the keys to be output

    if not args.no_keys:
        print(args.keys)
    if args.keys_only:
        sys.exit(0)

    # collect data and output results

    keys = args.keys.split(',')
    for path in args.paths:
        try:
            print(','.join(PbsReportParser(path).get_values(keys)))
        except ValueError as value_error:
            sys.stderr.write(str(value_error)+"\n")

if __name__ == "__main__":
    main()
