# Extending pbs_reporter.py

Possible extension to the current code

## sniff stderr file for errors

A small mod to ``pbs_reporter.py`` would allow the program to discover and interrogate the ``stderr`` file 
produced by ``PBS`` for each job. The reporter could

1. record the size of the file
1. run a ``regex`` over the file content and count the number of matches (e.g. ``regex='ERROR'``)

```
class StderrParser(object):
    """
    Sniffs into stderr file looking for errors
    """
    pat = re.compile("ERROR")
    def __init__(self, path):
        self.errors = 0
        self.stderr_lines = 0
        with open(path, 'r') as infile:
            for line in infile:
                self.stderr_lines += 1
                if self.pat.search(line) is not None:
                    self.errors += 1
        self.e_file_path = path
        self.stderr_size = os.path.getsize(path)
```

## handle non PBS stdout content

Many user programs write interesting information to ``stdout``. It would be good to capture this information and include it 
in the CSV output.

One approach is to write sub-classes of ``PbsReportParser`` that adds properties to the ``PbsReportParser`` instance.

```
class YourStdoutParser(PbsReportParser):
    """
    Extracts information reported by your program on stdout
    """

    my_pattern = re.compile((
        "^(?P<successful>\d+) successful,\s+(?P<failed>\d+) failed$"
        ), re.MULTILINE)

    def __init__(self, o_file_path):
        super(YourStdoutParser, self).__init__(o_file_path)
        self._parsefile(o_file_path, self.stacker_pattern)
        self.finished = datetime.utcfromtimestamp(os.path.getmtime(o_file_path)).isoformat()
        self.job_no = Path(o_file_path).stem
        self.o_file_path = o_file_path
```
