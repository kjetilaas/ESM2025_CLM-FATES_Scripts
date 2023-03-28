#!/bin/bash 

#Scrip to clone and checkout ctsm for ESM2025 simulations

dosetup=1 

# what is your clone of the ctsm repo called? (or you want it to be called?) 
ctsmdir="CTSM" 
checkout_version="ctsm5.1.dev118"

# aka where do you want the code and scripts to live?
projectfolder="/cluster/home/kjetisaa/ESM2025_CTSM/" 


#Download code and checkout externals
if [ $dosetup -eq 1 ] 
then
    cd $projectfolder

    pwd
    #go to repo, or checkout code
    if [[ -d "$ctsmdir" ]] 
    then
        cd $ctsmdir
        echo "Already have ctsm folder"
    else
        module purge
        module load git/2.18.0-GCCcore-7.3.0 Python/3.7.4-GCCcore-8.3.0

        echo "Cloning ctsm"
        #clone CTSM code if you didn't to this already. 
        git clone https://github.com/escomp/ctsm $ctsmdir
        cd $ctsmdir
        git checkout $checkout_version
        ./manage_externals/checkout_externals
        module purge
    fi
fi
