#!/bin/bash 


USER="kjetisaa"
project='nn9188k' #nn8057k: EMERALD, nn2806k: METOS, nn9188k: CICERO
machine='fram'
numCPUs=1024 #Specify number of cpus. 0: use default
forcenewcase=1 #what to do if case exists. 1: remove
model=UKESM1-0-LL


# Path to project folder 
projectfolder="/cluster/home/kjetisaa/ESM2025_CTSM/" 
casedir="/cluster/home/kjetisaa/ESM2025_CTSM/cases/"
cimedir="/cluster/home/kjetisaa/ESM2025_CTSM/CTSM/cime/scripts/"
usermodsdir="/cluster/work/users/kjetisaa/isimip_forc/historical/$model/user_mods/"

#Setup 
modelconfig="BGC-CROP" 
resolution='f19_g17' 
scenario="1850" 
versiontag=ADspinup
casename="Test_ESM2025_${modelconfig}_${scenario}_${resolution}_$versiontag"
compset="${scenario}_DATM%GSWP3v1_CLM51%${modelconfig}_SICE_SOCN_SROF_SGLC_SWAV_SESP"

stop_n="5"
stop_opt="nyears"
job_wc_time="48:00:00"
resub="0"  

if [[ $forcenewcase -eq 1 ]]
echo "here" 
echo $casedir$casename
then 
    if [[ -d "$casedir$casename" ]] 
    then    
    echo "$casedir$casename exists on your filesystem. Removing it!"
    rm -r /cluster/work/users/kjetisaa/ctsm/$casename
    rm -r /cluster/work/users/kjetisaa/archive/$casename
    rm -r $casedir$casename
    fi
fi


cd $cimedir
./create_newcase --case $casedir$casename --compset $compset --res $resolution  --run-unsupported --project $project --machine $machine --user-mods-dir $usermodsdir
cd $casedir$casename

#XML changes
echo 'updating settings'
./xmlchange CONTINUE_RUN=FALSE
./xmlchange --id STOP_N --val $stop_n
./xmlchange --id STOP_OPTION --val $stop_opt
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=$job_wc_time
./xmlchange CLM_ACCELERATED_SPINUP="on"
./xmlchange RESUBMIT=$resub
./xmlchange RUN_STARTDATE="0000-01-01"

./xmlchange DATM_YR_ALIGN=1851
./xmlchange DATM_YR_START=1851
./xmlchange DATM_YR_END=1869
./xmlchange CLM_USRDAT_DIR="/cluster/work/users/kjetisaa/isimip_forc/historical/$model/atm_forcing.datm7.GSWP3.0.5d.v1.c170516"

#./xmlchange DATM_YR_ALIGN=1901
#./xmlchange DATM_YR_START=1901
#./xmlchange DATM_YR_END=1910
#./xmlchange DIN_LOC_ROOT_CLMFORC='/cluster/work/users/kjetisaa/isimip_forc/historical/$model/'
if [[ $numCPUs -ne 0 ]]
then 
    echo "setting #CPUs to $numCPUs"
    ./xmlchange NTASKS_ATM=$numCPUs
    ./xmlchange NTASKS_OCN=$numCPUs
    ./xmlchange NTASKS_LND=$numCPUs
    ./xmlchange NTASKS_ICE=$numCPUs
    ./xmlchange NTASKS_ROF=$numCPUs
    ./xmlchange NTASKS_GLC=$numCPUs
fi
echo 'done with xmlchanges'        
    
./case.setup
./case.build
./case.submit
