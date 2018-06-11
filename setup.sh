#!/bin/bash

cvmfs_setup=/cvmfs/cms.cern.ch/cmsset_default.sh
if [ ! -f $cvmfs_setup ]; then
    echo "Need $cvmfs_setup to find the dasgoclient script"
    exit 1
fi

source $cvmfs_setup
voms-proxy-init -voms cms --valid 168:00

top_dir(){
  local Canonicalize="readlink -f"
  $Canonicalize asdf &> /dev/null || Canonicalize=realpath
  dirname "$($Canonicalize "${BASH_SOURCE[0]}")"
}

PYTHONPATH="${PYTHONPATH}:$(top_dir)/externals/xsecdb/scripts/wrapper/"
PATH="$PATH:$(top_dir)externals/xsecdb/scripts/wrapper/"
