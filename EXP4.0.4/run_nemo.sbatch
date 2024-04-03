#!/bin/bash
#SBATCH -p ib-64-512
#SBATCH --qos=ib
#SBATCH -o %j-nemo.out
#SBATCH -e %j-nemo.err
#SBATCH -t 02:00:00
#SBATCH --job-name=nemo
#SBATCH --ntasks=98

module purge
source ~/NEMO/NEMO_4.0.4_CO9_package_tides/add_mod_ada_intel.sh

mpirun ./nemo
