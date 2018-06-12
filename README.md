## CMS DAS Query

Example of how to run:
```
source setup.sh
python bin/dataset_query "/SingleMuon/*05Feb2018*/NANOAOD"
```

The help command gives:
```
Usage: dataset_query [OPTIONS] DATASET_QUERY

  Generate the dataframe with the dataset info

Options:
  -o, --out_file TEXT  The path to an output file. If it already exists, will
                       append to this file.
  -i, --instance TEXT  Instance to be passed to the dasgoclient query
  --do-xsdb-query      Query XSDB for XS
  --help               Show this message and exit.
```

From your python script you can also do:
```
import cms_das_query.das_query as das_query
dataframe = das_query("/SingleMuon/*05Feb2018*/NANOAOD")
```

### With XSDB query:
1. Make sure the xsdb code was checked out (it's a submodule of this one):
   * `git submodule update`
2. source this setup.sh script
3. make sure you've got the necessary python packages, eg pycurl
