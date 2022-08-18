#!/bin/zsh

TF_PATH=${PWD}/$1

cd $TF_PATH;
tfswitch --chdir="$TF_PATH";

# initialise terraform state if necessary
if [ ! -d ./.terraform ]; then
  terraform init -backend=false -upgrade
fi

terraform validate