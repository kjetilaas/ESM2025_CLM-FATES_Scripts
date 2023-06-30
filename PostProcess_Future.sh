#!/bin/bash
module load CDO/1.9.10-gompi-2020b

# define paths
model=UKESM1-0-LL #IPSL-CM6A-LR, MPI-ESM1-2-HR, UKESM1-0-LL
scenario="SSP126"

# loop over experiments:
experiments=("noluc" "agtonat" "agtoaff" "nattoaff" "agtobio" "nattobio")
#experiments=("noluc")

# begin loop
for experiment in "${experiments[@]}"
do
    resultsdir="/cluster/work/users/kjetisaa/archive/ESM2025_${model}_BGC-CROP_${scenario}_f19_g17_$experiment/lnd/hist"
    filenames="ESM2025_${model}_BGC-CROP_${scenario}_f19_g17_$experiment.clm2.h0.*.nc"
    outdir="/cluster/work/users/kjetisaa/PostProcessed_archive/$model/$experiment/"
    
    # make outdir if it does not exist
    mkdir -p "$outdir"
    
    # produce one file per variable for the following variables:
    #variables=("TOTSOMC" "TOTSOMC_1m" "TOTVEGC" "TOTECOSYSC" "NBP" "GPP" "NPP" "TSA")
    #variables=("TOTSOMC")
    
    variables="TOTSOMC,TOTSOMC_1m,TOTVEGC,TOTECOSYSC,NBP,GPP,NPP,TSA"
    #for variable in "${variables[@]}"
    #do
    #    echo $variable
    #    echo "cdo -O -mergetime -apply,-selvar,$variable,area [ $resultsdir/$filenames ] $outdir/$variable.nc"
    #done
    cdo -O -mergetime -apply,-selvar,$variables,area,landfrac [ $resultsdir/$filenames ] $outdir/ESM2025_${scenario}_$experiment.nc
done

# end experiment loop