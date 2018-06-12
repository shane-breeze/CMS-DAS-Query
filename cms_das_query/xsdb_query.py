import os
import sys
import shlex
from subprocess import Popen
from subprocess import PIPE

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def xsdb_query(data, attrs=["shower", "mtrx_gen", "cross_section", "accuracy"]):
    """
    Query XSDB webpage for dataset infos. Currently requires kerberos
    authentication to work (i.e. only works on lxplus)

    :data: List of dicts for each dataset with various information
    :attrs: Attributes to search for in the XSDB query
    """
    # Loop over dataset querying using the "process_name"
    for dataset in data:
        process_name = dataset["dataset"]
        query = {"process_name": process_name}

        # I would very much appreciate it if people would write their code so
        # that a result is returned from a function rather than printing the
        # result to stdout. Rant over
        command = "python -c \"from request_wrapper import RequestWrapper; RequestWrapper().simple_search({})\"".format(query)
        p = Popen(shlex.split(command), stdout=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate()
        if not (stdout or stderr) or "error" in "{}{}".format(stdout,stderr).lower():
            logging.error("Problem querying XSDB. Switching off XSDB query. Note that this is only supported on lxplus")
            return data
        else:
            result = eval(stdout)

        # len(result)==0 if there is no xsdb entry. Need to use the genXS tool
        if len(result)==0:
            logging.warning("No entry found for {}. Try using the genXS tool".format(process_name))
        else:
            for k in attrs:
                dataset[k] = result[0][k]

    return data
