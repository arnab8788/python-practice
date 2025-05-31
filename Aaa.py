#!/bin/bash

export LANG=en_US.ISO8859-1
export INF_PWD_FILE_NAME=.105_INF_PWD
export PATH=$PATH:/opt/informatica/pc105/server/bin
export LD_LIBRARY_PATH=/opt/informatica/pc105/server/bin:$LD_LIBRARY_PATH
export INFA_HOME=/opt/informatica/pc105
export INF_PWD_FILE=/UNX2_INF/SCRIPTS/$INF_PWD_FILE_NAME
export INF_USER=Administrator
export INF_PWD=$(cat $INF_PWD_FILE)
export INF_DOMAIN_DEV=Dev_EVG_Domain
export INF_SVC_NAME_DEV=dev_evg_repo_DIME
export INF_SVC_NAME=$INF_SVC_NAME_DEV

pmrep connect -r $INF_SVC_NAME -d $INF_DOMAIN_DEV -n $INF_USER -X INF_PWD -codepage ISO_8859_1
pmrep objectexport -o workflow -n "wf_EDL_GCI_Address_Extract" -f "EDLExtracts" -m -u "/DATA_INF/JHIM/INFORMATICA/SRCFILES/DATAFEED/wf_EDL_GCI_Address_Extract.xml" -m -s -b -r -l "/DATA_INF/JHIM/INFORMATICA/SRCFILES/DATAFEED/pmrep.log"
pmrep disconnect

export LANG=en_US.UTF-8

