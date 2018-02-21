## CMS DAS Query

Example of how to run:
```
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
