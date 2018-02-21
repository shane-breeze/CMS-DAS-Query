import os
import shlex
from subprocess import Popen
from subprocess import PIPE

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

import pandas as pd
pd.set_option('display.max_colwidth', -1)

from xsdb_query import xsdb_query

DASGOCLIENT_TEMPALTE = 'dasgoclient --query "{command} dataset={dataset} instance={instance}" --limit 0'

def run_command(command, dry_run=False):
    """
    Pass a bash command as a string to run. No stdin
    """
    p = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE)
    return p.communicate()

def dataset_info_query(dataset, instance):
    """
    Collect the results of the 'summary' and 'file' command in dasgoclient for
    the input dataset.
    """
    summary_command = DASGOCLIENT_TEMPALTE.format(
        command  = "summary",
        dataset  = dataset,
        instance = instance,
    )
    out, err = run_command(summary_command)

    # Convert string to dictionary
    # e.g.
    # out = b"[{"file_size":38240056782,"nblocks":11,"nevents":90963495,"nfiles":42,"nlumis":26865,"num_block":11,"num_event":90963495,"num_file":42,"num_lumi":26865}]"
    summary = eval(out)[0]
    # summary = {"file_size":38240056782,"nblocks":11,"nevents":90963495,"nfiles":42,"nlumis":26865,"num_block":11,"num_event":90963495,"num_file":42,"num_lumi":26865}

    files_command = DASGOCLIENT_TEMPALTE.format(
        command  = "file",
        dataset  = dataset,
        instance = instance,
    )
    out, err = run_command(files_command)

    # Convert '\n' delimited string into list of strings containing each file
    # location
    files = out.split()

    return summary, files

def das_query(dataset_query,
              out_file=None,
              instance="prod/global",
              do_xsdb_query=False):
    """
    Creates a dataframe from DAS and XSDB queries. 1 dataset per row.

    Saves the dataframe to out_file (if specified). If the file exists, will
    append to this file.
    """

    dataset_command = DASGOCLIENT_TEMPALTE.format(
        command  = "dataset",
        dataset  = dataset_query,
        instance = instance,
    )
    out, err = run_command(dataset_command)

    # Convert '\n' delimited string into list of strings containing each dataset
    datasets = out.split()

    data = []
    for dataset in datasets:
        logging.info(dataset)
        dataset_name, era, tier = dataset.split("/")[1:]
        event_type = "MC" if "SIM" in tier else "Data"
        summary, files = dataset_info_query(dataset, instance)

        data.append({
            "eventtype": event_type,
            "dataset": dataset_name,
            "era": era,
            "nevents": summary["nevents"],
            "nfiles": summary["nfiles"],
            "files": files,
            })

    df = pd.DataFrame(data, columns=["eventtype", "dataset", "era", "nevents", "nfiles", "files"])
    mc_attrs = ["mtrx_gen","shower","cross_section","accuracy"]
    if do_xsdb_query:
        df = xsdb_query(df,attrs=mc_attrs) # Add NANs to data / non-existent xsdb queries
        df = df[["eventtype","dataset","era","nevents","nfiles"]+mc_attrs+["files"]]

    if out_file is not None:
        if os.path.exists(out_file):
            df_existing = pd.read_table(out_file,sep='\s+',comment='#')
            df_existing["files"] = df_existing["files"].apply(eval)
            df = pd.concat([df_existing, df]).reset_index(drop=True)
        with open(out_file,'w') as f:
            df.update(df[["files"]].applymap('"{}"'.format))
            f.write(df.to_string())
    logging.info(df.drop(["files"],axis=1))
    return df

if __name__ == "__main__":
    df = das_query("/SingleMuon/*/NANOAOD")
    print df
