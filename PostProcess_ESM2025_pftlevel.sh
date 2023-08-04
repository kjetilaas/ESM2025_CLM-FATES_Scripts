#!/bin/bash
#This script is used as an intermediate step to produce one file pr variable which can be further 
#post processed with "PostProcess_Future_PFTlevel.py". 

#module load CDO/1.9.8-intel-2019b NCO/4.9.3-intel-2019b 
module load CDO/1.9.10-gompi-2020b 

models=("UKESM1-0-LL" ) #"IPSL-CM6A-LR" "MPI-ESM1-2-HR"
scenarios=("SSP126" ) # ("HIST") "SSP370"
experiments=("_noluc" ) #("") "_agtonat" "_agtoaff" "_nattoaff" "_agtobio" "_nattobio"
vars_cdo="TOTVEGC,GPP,NPP,TLAI,FCTR,NBP,TV,HTOP"
variables=("TOTVEGC" "GPP" "NPP" "TLAI" "FCTR" "NBP" "TV" "HTOP")

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
            resultsdir="/cluster/work/users/kjetisaa/archive/ESM2025_${model}_BGC-CROP_${scenario}_f19_g17$experiment/lnd/hist"
            #resultsdir="/cluster/work/users/kjetisaa/archive/ESM2025_${model}_BGC-CROP_${scenario}_f19_g17_historical/lnd/hist"
            filenames="ESM2025_${model}_BGC-CROP_${scenario}_f19_g17$experiment.clm2.h1.*.nc"
            outdir="/cluster/work/users/kjetisaa/PostProcessed_archive/Temp_results_PFTlevel/"
            
            # make outdir if it does not exist
            mkdir -p "$outdir"
            
            cdo -O -mergetime -apply,-selvar,"$vars_cdo" [ $resultsdir/$filenames ] "$outdir/clm_${model_lowercase}_${scenario_lowercase}${experiment}_ALL.monthly.h1_RAW.nc_tmp"

            # produce one file per variable:
            for ((i=0; i<${#variables[@]}; i++))
            do                
                variable="${variables[i]}"                
                echo "$variable"                                                
                cdo -selvar,$variable "$outdir/clm_${model_lowercase}_${scenario_lowercase}${experiment}_ALL.monthly.h1_RAW.nc_tmp" "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_${variable}.monthly.h1_RAW.nc"
            done        
            
            rm "$outdir/clm_${model_lowercase}_${scenario_lowercase}${experiment}_ALL.monthly.h1_RAW.nc_tmp"
        done
    done
done
