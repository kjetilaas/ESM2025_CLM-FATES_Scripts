#!/bin/bash 

#Scrip to clone and checkout ctsm for ESM2025 simulations

# what is your clone of the ctsm repo called? (or you want it to be called?) 
ctsmdir="ESM2025_noresmhub" 
checkout_version="ctsm5.1.dev123-noresm_v1"

#Download code and checkout externals
cd "/cluster/work/users/kjetisaa"

#Remove old ctsm code  
rm -rf $ctsmdir

if [[ -d "$ctsmdir" ]] 
then
    cd $ctsmdir
    echo "Already have $ctsmdir folder, do a git pull"
    git pull
else
    module purge
    module load git/2.36.0-GCCcore-11.3.0-nodocs
    #module load git/2.23.0-GCCcore-8.3.0 Python/3.7.4-GCCcore-8.3.0

    echo "Cloning ctsm"
    
    git clone https://github.com/NorESMhub/CTSM $ctsmdir
    cd $ctsmdir 
    git checkout $checkout_version
    
    ./manage_externals/checkout_externals
    module purge
fi
