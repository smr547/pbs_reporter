# pbs_reporter.py

Extract PBS job statistics from a list of stdout files and list them as CSV stream

## usage

```
usage: pbs_reporter.py [-h] [-k KEYS] [--keys_only] [--no_keys]
                       [paths [paths ...]]

Collect and output PBS job statistics

positional arguments:
  paths                 paths to PBS output files

optional arguments:
  -h, --help            show this help message and exit
  -k KEYS, --keys KEYS  comma separated list of keys
  --keys_only           print the keys to be output
  --no_keys             supress the output of keys
```

## Example

```
find /g/data/v10/tmp/pq-stack -name *.o* | xargs python ./job_reporter.py --keys 'job_id,ncpus_requested,ncpus_used,cpu_used,walltime_used,cpu_utilisation,exit_status,cpu_used_secs' > example.csv
``` 

see [sample.csv](./sample.csv)
