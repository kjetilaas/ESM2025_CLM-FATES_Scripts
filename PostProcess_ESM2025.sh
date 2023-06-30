#!/bin/bash
#module load CDO/1.9.8-intel-2019b NCO/4.9.3-intel-2019b 
module load CDO/1.9.10-gompi-2020b 

models=("UKESM1-0-LL" "IPSL-CM6A-LR" "MPI-ESM1-2-HR")
scenarios=("SSP126" "SSP370") # ("HIST")
experiments=("_noluc" "_agtonat" "_agtoaff" "_nattoaff" "_agtobio" "_nattobio") #("")
vars_cdo="TOTSOMC,TOTVEGC,GPP,NPP,HR,AR,TLAI"

#carbon variables (to be converted from g to kg)
variables_c=("TOTSOMC" "TOTVEGC" "GPP" "NPP" "HR" "AR")
variables_c_new=("cSoil" "cVeg" "gpp" "npp" "hr" "ar")

#non c cariables 
variables=("TLAI")
variables_new=("lai")

fc_vars=("gpp" "npp" "hr" "ar")
c_vars=("cSoil" "cVeg")

#Convert from g to kg:
conversion_factor=0.001

#Full list of variables (from JULES):
#AlbedoNIRpft,AlbedoVispft,burntArea,cLeafpft,cRootpft,cSoil,cSoilpools,cVeg,cVegpft,cWoodpft,
#evapo,evapotrans,evapotranspft,evpsblveg,evspsblsoi,fBioHarvestpft,fBNF,fFireCsoil,fFireCveg,
#fFireLitter,fHarvest,fHeatLatent,fHeatSensible,fHeatSensiblepft,fLeafLitter,fNBioHarvestpft,
#fNdep,fNimmob,fNloss,fNup,fRootLitter,fVegLitter,fWoodLitter,gpp,gpppft,lai,laipft,landCoverFrac

# begin loop
for model in  "${models[@]}"
do
    model_lowercase=$(echo "$model" | tr '[:upper:]' '[:lower:]')  # Convert model name to lowercase
    for scenario in "${scenarios[@]}"
    do
        scenario_lowercase=$(echo "$scenario" | tr '[:upper:]' '[:lower:]')  # Convert scenario name to lowercase
        for experiment in "${experiments[@]}"
        do
            #resultsdir="/cluster/work/users/kjetisaa/archive/ESM2025_${model}_BGC-CROP_${scenario}_f19_g17$experiment/lnd/hist"
            resultsdir="/cluster/work/users/kjetisaa/archive/ESM2025_${model}_BGC-CROP_${scenario}_f19_g17_historical/lnd/hist"
            filenames="ESM2025_${model}_BGC-CROP_${scenario}_f19_g17$experiment.clm2.h0.*.nc"
            outdir="/cluster/work/users/kjetisaa/PostProcessed_archive/ESM2025_WP10_postprocessed/"
            
            # make outdir if it does not exist
            mkdir -p "$outdir"
            
            cdo -O -mergetime -apply,-selvar,"$vars_cdo" [ $resultsdir/$filenames ] "$outdir/clm_${model_lowercase}_${scenario_lowercase}${experiment}_ALL.monthly.nc_tmp"

            # produce one file per variable:
            for ((i=0; i<${#variables_c[@]}; i++))
            do                
                variable="${variables_c[i]}"
                variable_new="${variables_c_new[i]}"
                echo "$variable"                                                
                cdo -chname,$variable,$variable_new -selvar,$variable -mulc,$conversion_factor "$outdir/clm_${model_lowercase}_${scenario_lowercase}${experiment}_ALL.monthly.nc_tmp" "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_${variable_new}.monthly.nc"
            done        

            # produce one file per variable:
            for ((i=0; i<${#variables[@]}; i++))
            do                
                variable="${variables[i]}"
                variable_new="${variables_new[i]}"
                echo "$variable"                                                
                cdo -chname,$variable,$variable_new -selvar,$variable -mulc,$conversion_factor "$outdir/clm_${model_lowercase}_${scenario_lowercase}${experiment}_ALL.monthly.nc_tmp" "$outdir/clm_${model_lowercase}_${scenario_lowercase}_${experiment}_${variable_new}.monthly.nc"
            done 
            rm "$outdir/clm_${model_lowercase}_${scenario_lowercase}${experiment}_ALL.monthly.nc_tmp"
        done
    done
done

module purge
module load NCO/4.9.3-intel-2019b

#carbon fluxes
for var in  "${fc_vars[@]}"
do
    echo $var
    for file in $outdir/*$var*nc
    do
        echo $file
        ncatted -O -a units,"${var}",m,c,"kg m-2 s-1" $file
    done
done

#carbon pools
for var in  "${c_vars[@]}"
do
    echo $var
    for file in $outdir/*$var*nc
    do
        echo $file
        ncatted -O -a units,"${var}",m,c,"kg m-2" $file
    done
done