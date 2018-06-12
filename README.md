## CMS DAS Query

### Output

When run properly, the code in this repository should query the CMS DAS (and
possible XSDB) database to get information on datasets. The standard output is
```
INFO:/SingleMuon/Run2016H-03Feb2017_ver2-v1/MINIAOD
INFO:/SingleMuon/Run2016H-03Feb2017_ver3-v1/MINIAOD
INFO:
[{'dataset': 'SingleMuon',
  'era': 'Run2016H-03Feb2017_ver2-v1',
  'eventtype': 'Data',
  'nevents': 169642135,
  'nfiles': 1201},
 {'dataset': 'SingleMuon',
  'era': 'Run2016H-03Feb2017_ver3-v1',
  'eventtype': 'Data',
  'nevents': 4393029,
  'nfiles': 30}]
```

It will also save the result in various formats of your choice: pandas, yaml,
json or pickle.

### How to run

Example of how to run:
```
source setup.sh
das_query "/SingleMuon/*05Feb2018*/NANOAOD" -f yaml
```

The help command gives:
```
usage: das_query [-h] [-o OUT_FILE] [-i INSTANCE] [-f FORM] [--do-xsdb-query]
                 dataset_query

positional arguments:
  dataset_query

optional arguments:
  -h, --help            show this help message and exit
  -o OUT_FILE, --out_file OUT_FILE
                        The path to an output file. If it already exists, will
                        append to this file.
  -i INSTANCE, --instance INSTANCE
                        Instance to be passed to the dasgoclient query
  -f FORM, --form FORM  Format of the output file
  --do-xsdb-query       Query XSDB for XS
```

From your python script you can also do:
```
import cms_das_query.das_query as das_query
dataframe = das_query("/SingleMuon/*05Feb2018*/NANOAOD", form="json")
```

### With XSDB query:

1. Make sure the xsdb code was checked out (it's a submodule of this one):
   * `git submodule update`
2. source this setup.sh script
3. make sure you've got the necessary python packages, eg pycurl
