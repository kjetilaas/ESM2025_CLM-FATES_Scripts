#!/bin/bash 


USER="kjetisaa"
project='nn9188k' #nn8057k: EMERALD, nn2806k: METOS, nn9188k: CICERO
machine='betzy'
numCPUs=1024 #Specify number of cpus. 0: use default
forcenewcase=1 #what to do if case exists. 1: remove
model=UKESM1-0-LL #IPSL-CM6A-LR, MPI-ESM1-2-HR, UKESM1-0-LL


cimedir="/cluster/work/users/kjetisaa/ESM2025/cime/scripts/"
usermodsdir="/cluster/work/users/kjetisaa/isimip_forc/historical/$model/user_mods/"
casedir="/cluster/work/users/kjetisaa/ESM2025/cases/$model/"
mkdir -p $casedir

#Setup 
modelconfig="BGC-CROP" 
resolution="f19_g17" 
scenario="HIST" 
versiontag="historical"
casename="ESM2025_${model}_${modelconfig}_${scenario}_${resolution}_$versiontag"
compset="${scenario}_DATM%GSWP3v1_CLM51%${modelconfig}_SICE_SOCN_SROF_SGLC_SWAV_SESP"
casename_postAD="ESM2025_${model}_${modelconfig}_${scenario}_${resolution}_ADspinup"

stop_n="55"
stop_opt="nyears"
job_wc_time="48:00:00"
resub="2" 
lastrestarttime="1000-01-01-00000" 

if [[ $forcenewcase -eq 1 ]]
echo $casedir$casename
then 
    if [[ -d "$casedir$casename" ]] 
    then    
    echo "$casedir$casename exists on your filesystem. Removing it!"
    rm -r /cluster/work/users/kjetisaa/noresm/$casename
    rm -r /cluster/work/users/kjetisaa/archive/$casename
    rm -r $casedir$casename
    fi
fi

cd $cimedir
./create_newcase --case $casedir$casename --compset $compset --res $resolution  --run-unsupported --project $project --machine $machine --handle-preexisting-dirs r --mpilib impi --user-mods-dir $usermodsdir

cd $casedir$casename

#XML changes
echo 'updating settings'
./xmlchange CONTINUE_RUN=FALSE
./xmlchange --id STOP_N --val $stop_n
./xmlchange --id STOP_OPTION --val $stop_opt
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=$job_wc_time
./xmlchange RESUBMIT=$resub
./xmlchange RUN_STARTDATE="1850-01-01"
./xmlchange DATM_YR_ALIGN=1850
./xmlchange DATM_YR_START=1850
./xmlchange DATM_YR_END=2014
./xmlchange CLM_USRDAT_DIR="/cluster/work/users/kjetisaa/isimip_forc/historical/$model"


echo "flanduse_timeseries='/cluster/work/users/kjetisaa/isimip_forc/Ohter_modified_files/landuse.timeseries_1.9x2.5_hist_78pfts_CMIP6_simyr1850-2015_ESM2025.nc'" >> user_nl_clm
echo "fsurdat='/cluster/work/users/kjetisaa/isimip_forc/Ohter_modified_files/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr1850_ESM2025.nc'" >> user_nl_clm
echo "use_init_interp=.true." >> user_nl_clm

# copy restart files and pointers
cp /cluster/work/users/kjetisaa/archive/$casename_AD/rest/$lastrestarttime/*clm.r*.nc /cluster/work/users/kjetisaa/noresm/$casename/run/
cp /cluster/work/users/kjetisaa/archive/$casename_AD/rest/$lastrestarttime/rpointer.atm /cluster/work/users/kjetisaa/noresm/$casename/run/
echo 'List files in run folder (after copy restart):'
ls -l /cluster/work/users/kjetisaa/noresm/$casename/run/

# Set the finidat file to the last restart file saved in previous step
echo " finidat = '${casename_AD}.clm2.r.$lastrestarttime.nc' " >> user_nl_clm

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
