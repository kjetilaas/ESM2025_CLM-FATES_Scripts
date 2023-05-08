#!/bin/bash 


USER="kjetisaa"
project='nn9188k' #nn8057k: EMERALD, nn2806k: METOS, nn9188k: CICERO
machine='betzy'
forcenewcase=1 #what to do if case exists. 1: remove
model=UKESM1-0-LL #IPSL-CM6A-LR, MPI-ESM1-2-HR, UKESM1-0-LL


cimedir="/cluster/work/users/kjetisaa/ESM2025_noresmhub/cime/scripts/"
usermodsdir="/cluster/work/users/kjetisaa/isimip_forc/historical/$model/user_mods/"
casedir="/cluster/work/users/kjetisaa/ESM2025_noresmhub/cases/$model/"
mkdir -p $casedir

#Setup 
modelconfig="BGC-CROP" 
resolution="f19_g17" 
scenario="1850" 
versiontag="ADspinup"
casename="TestM05_ESM2025_${model}_${modelconfig}_${scenario}_${resolution}_${versiontag}"
compset="${scenario}_DATM%GSWP3v1_CLM51%${modelconfig}_SICE_SOCN_SROF_SGLC_SWAV_SESP"

stop_n="5"
stop_opt="nyears"
job_wc_time="02:00:00"
resub="0"  
starttime="0001-01-01"

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
./create_newcase --case $casedir$casename --compset $compset --res $resolution  --run-unsupported --project $project --machine $machine --handle-preexisting-dirs r --user-mods-dir $usermodsdir --pecount M

cd $casedir$casename

#XML changes
echo 'updating settings'
./xmlchange CONTINUE_RUN=FALSE
./xmlchange --id STOP_N --val $stop_n
./xmlchange --id STOP_OPTION --val $stop_opt
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=$job_wc_time
./xmlchange CLM_ACCELERATED_SPINUP="on"
./xmlchange RESUBMIT=$resub
./xmlchange DATM_YR_ALIGN=1850
./xmlchange DATM_YR_START=1850
./xmlchange DATM_YR_END=1869
./xmlchange CLM_USRDAT_DIR="/cluster/work/users/kjetisaa/isimip_forc/historical/$model"
./xmlchange RUN_STARTDATE=$starttime

echo "flanduse_timeseries='/cluster/work/users/kjetisaa/isimip_forc/Ohter_modified_files/landuse.timeseries_1.9x2.5_hist_78pfts_CMIP6_simyr1850-2015_ESM2025.nc'" >> user_nl_clm
echo "fsurdat='/cluster/work/users/kjetisaa/isimip_forc/Ohter_modified_files/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr1850_ESM2025.nc'" >> user_nl_clm
echo "use_init_interp=.true." >> user_nl_clm
echo "stream_fldfilename_ndep = '/cluster/work/users/kjetisaa/isimip_forc/Ohter_modified_files/fndep_clm_hist_b.e21.BWHIST.f09_g17.CMIP6-historical-WACCM.ymonavg_1850-1869_monthly_0.9x1.25_ESM2025.nc'" >> user_nl_clm

echo 'done with xmlchanges'        
    
./case.setup
./case.build
./case.submit
