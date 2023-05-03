#!/bin/bash 

#Scrip to clone and checkout ctsm for ESM2025 simulations

# what is your clone of the ctsm repo called? (or you want it to be called?) 
ctsmdir="ESM2025" 
checkout_version="stable_sigma2" #"ctsm5.1.dev120"

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
    #clone CTSM code if you didn't to this already. 
    #git clone https://github.com/escomp/ctsm $ctsmdir
    #cd $ctsmdir
    #git checkout $checkout_version
    #cp ../../CTSM/Externals.cfg .  #Temporary fix for betzy
    #git clone https://github.com/mvertens/CTSM
    #cd CTSM
    #git checkout feature/update_ccs_config
    
    git clone https://github.com/MetOs-UiO/CTSM.git $ctsmdir
    cd $ctsmdir
    git checkout $checkout_version
    
    ./manage_externals/checkout_externals
    module purge
fi
