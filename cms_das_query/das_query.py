import os
import shlex
from subprocess import Popen
from subprocess import PIPE
from pprint import pformat, pprint
import importlib

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

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

def create_output(result, outfile, form="json"):
    """
    Create the output in a specific format (form). Try to import the module for
    the output format going down the chain until one is found:
        pandas -> yaml -> json -> pickle
    """

    chain = {
        "pandas": "yaml",
        "yaml": "json",
        "json": "pickle",
    }
    form_kwargs = {
        "yaml": {},
        "json": {"indent": 2, "sort_keys": True},
        "pickle": {},
    }

    while True:
        try:
            module = importlib.import_module(form)
        except ImportError:
            if form not in chain:
                logging.info("Failed to import any output format")
                return
            new_form = chain[form]
            logging.info(
                "Could not import {}. Using {} instead".format(
                    form,
                    new_form,
                )
            )
            form = new_form
        else:
            break

    # Deal with pandas separately
    if form == "pandas":
        module.set_option('display.max_colwidth', -1)
        df = module.DataFrame(result)
        df.update(df[["files"]].applymap('"{}"'.format))
        outfile.write(df.to_string())
    else:
        module.dump(result, outfile, **form_kwargs[form])

def das_query(dataset_query,
              out_file=None,
              instance="prod/global",
              do_xsdb_query=False,
              form="pickle"):
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

    if do_xsdb_query:
        mc_attrs = ["mtrx_gen","shower","cross_section","accuracy"]
        data = xsdb_query(data, attrs=mc_attrs) # Add NANs to data / non-existent xsdb queries

    if out_file is not None:
        out_dir = os.path.dirname(out_file)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(out_file,'w') as f:
            create_output(data, f, form=form)

    # pformat creates the nice print of pprint but returns the string instead
    # of sending it to stdout
    logging.info(
        "\n" + pformat(
            [{k: v for k, v in d.items() if k != "files"} for d in data]
        )
    )
    return data

if __name__ == "__main__":
    data = das_query("/SingleMuon/*/NANOAOD")
    pprint(df)
