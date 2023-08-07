#!/bin/bash
#This script is used as an intermediate step to produce one file pr variable which can be further 
#post processed with "PostProcess_Future_PFTlevel.py". 

#module load CDO/1.9.8-intel-2019b NCO/4.9.3-intel-2019b 
module load CDO/1.9.10-gompi-2020b 

models=("UKESM1-0-LL" "IPSL-CM6A-LR" "MPI-ESM1-2-HR") #"IPSL-CM6A-LR" "MPI-ESM1-2-HR"
scenarios=("SSP126"  "SSP370") # ("HIST") "SSP370"
experiments=("noluc" "nattobio" "agtonat" "agtoaff" "nattoaff" "agtobio") 
vars_cdo="TV,TOTVEGC,GPP,NPP,TLAI,FCTR,HTOP" #NBP, TV,
variables=("TV" "TOTVEGC" "GPP" "NPP" "TLAI" "FCTR" "HTOP") #"NBP" 

#Full list of variables (from JULES):
#AlbedoNIRpft,AlbedoVispft,burntArea,cLeafpft,cRootpft,cSoil,cSoilpools,cVeg,cVegpft,cWoodpft,
#evapo,evapotrans,evapotranspft,evpsblveg,evspsblsoi,fBioHarvestpft,fBNF,fFireCsoil,fFireCveg,
#fFireLitter,fHarvest,fHeatLatent,fHeatSensible,fHeatSensiblepft,fLeafLitter,fNBioHarvestpft,
#fNdep,fNimmob,fNloss,fNup,fRootLitter,fVegLitter,fWoodLitter,gpp,gpppft,lai,laipft,landCoverFrac

# begin loop
for model in  "${models[@]}"
do
    echo $model
    model_lowercase=$(echo "$model" | tr '[:upper:]' '[:lower:]')  # Convert model name to lowercase
    for scenario in "${scenarios[@]}"
    do
        echo $scenario
        scenario_lowercase=$(echo "$scenario" | tr '[:upper:]' '[:lower:]')  # Convert scenario name to lowercase
        for experiment in "${experiments[@]}"
        do
            echo $experiment
            resultsdir="/cluster/work/users/kjetisaa/archive/ESM2025_${model}_BGC-CROP_${scenario}_f19_g17_$experiment/lnd/hist"
            filenames="ESM2025_${model}_BGC-CROP_${scenario}_f19_g17_$experiment.clm2.h1.*.nc"
            outdir="/cluster/work/users/kjetisaa/PostProcessed_archive/Temp_results_PFTlevel/"
            
            # make outdir if it does not exist
            mkdir -p "$outdir"
            
            cdo -O -s --no_warnings -mergetime -apply,-selvar,"$vars_cdo" [ $resultsdir/$filenames ] "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_ALL.monthly.h1_RAW.nc_tmp"

            # produce one file per variable:
            for ((i=0; i<${#variables[@]}; i++))
            do                
                variable="${variables[i]}"                
                echo "$variable"                                                
                cdo -selvar,$variable "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_ALL.monthly.h1_RAW.nc_tmp" "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_${variable}.monthly.h1_RAW.nc"
                #cdo -O -mergetime -apply,-selvar,"$variable" [ $resultsdir/$filenames ]  "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_${variable}.monthly.h1_RAW.nc"
            done        
            
            rm "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_ALL.monthly.h1_RAW.nc_tmp"
        done
    done
done
