# set input paths to those provided here: https://github.com/CefasRepRes/CO_AMM15

INPUT=/gpfs/data/cefas-shared/NEMO/jmmp/AMM15/

ln -s ${INPUT}/COORDINATES/CO9_rimwidth_9_coordinates.bdy_baltic.nc .
ln -s ${INPUT}/COORDINATES/amm15.bdy.coordinates.rim15.nc .
ln -s ${INPUT}/DOMAIN_CFG/GEG_SF12.nc .
ln -s ${INPUT}/RESTARTS/P15b/ini_GEG_NICOBALS.nc .
ln -s ${INPUT}/RESTARTS/P15b/ini_GEG_NICOBALT.nc .
ln -s ${INPUT}/FORCING/RIVERS/ ./RIV
ln -s ${INPUT}/FORCING/BDY/ .
ln -s ${INPUT}/FORCING/SBC/ .
ln -s ${INPUT}/FORCING/TIDES/ .

mkdir RESTARTS

