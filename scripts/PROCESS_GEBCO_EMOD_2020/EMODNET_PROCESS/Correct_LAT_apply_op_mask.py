"""  Script to  apply LAT correction and enforce mask from operational AMM15

 Original LSM is developed in AMM15_EMODNET_LSM_v2.py 
 Coordinates come from amm15_coord.py

 Variables needed in nemo bathy file are:
 bathymetry (metres)
 lat/lon - unrotated (gphi/glam)
 zenv? (only pre-v3.6?)
Parameters
----------
OP_LSM : str
    The location of the operational LSM e.g. EMODNET_LSM_v2.nc (create by J graham from EMODNET to AMM15 plus fill in lakes etc)
CS3X_CS20: str
    The location of the merged Surge data for LAT correction (valid only on AMM15 inner domain)
BATHY_DATA: str
    THe location the EMODNET data on the extended AMM15 grid
LAT_LON: str
    The location odf the file containinf the extended AMM15 domain lat lon grid
OUT_FILE: str
    Where to write the final output file after processing.

Returns
-------
iris cube
    The bathymetry in cube format
"""

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import time

from pathlib import Path
import argparse, sys

import sys, platform

from datetime import datetime
import subprocess



##=== Parse arguments
parser = argparse.ArgumentParser(description='Process inputs and output file paths')
parser.add_argument('-o','--OP_LSM', metavar='Operational LSM file', nargs=1,
                    help='File location of Operational AMM15 LSM', required=True)
parser.add_argument('-c','--CS3X_CS20',metavar='CS3X_CS20',  nargs=1,
                    help='File Locationof CS3X_CS20 LAT', required=True)
parser.add_argument( '-b','--BATHY_DATA',metavar='BATHY_DATA', nargs=1,
                    help='Path to output to ', required=True)
parser.add_argument( '-l','--LAT_LON',metavar='LAT_LON', nargs=1,
                    help='Path to coordinates file with lat lon ', required=True)
parser.add_argument( '-f','--OUT_FILE',metavar='OUT_FILE', nargs=1,
                    help='Path output file ', required=True)

args = parser.parse_args()

print("\n----------------------------------------------------\n")

print( "Thanks, you have chosen: \n ")

for arg in vars(args):
  print(" {} as --{}".format(getattr(args,arg)[0],arg) )
  print( arg)
  if arg !=  'OUT_FILE':
    if Path(getattr(args,arg)[0]).is_file():
       print(" and the file {} exists. \n".format (getattr(args,arg)[0]))
    else:
      sys.exit("However, {} does not exist so we exit here".format(getattr(args,arg)[0]))
#========================= end of arguments parsing


op_lsm_file = Dataset((args.OP_LSM)[0],'r')
op_lsm_bath = op_lsm_file.variables['Bathymetry'][:,:]

# NB. nemo interprets any point <= 0 as land (sets mbathy = 0)
# For now, convert any point <=0 to 1e-3, then sets nan values = 0.
# NEMO will convert these to the min depth variable for now.
# Will need to consider changing this method when W&D comes in...

cs3xcs20 = Dataset((args.CS3X_CS20)[0],'r')
cs3xcs20_bathy = cs3xcs20.variables['sea_floor_depth_below_geoid'][:,:]

input_dataset = Dataset((args.BATHY_DATA)[0],'r')
input_bathy = -input_dataset.variables['sea_floor_depth_below_geoid'][:,:]
input_bathy[np.where(input_bathy[:]<-100000)] = 'NaN'
inflate_lat = 100
inflate_lon = 100

# Thus we effectively have a core part of the domain and an outer part


input_bathy_amm15core = input_bathy[inflate_lat:-inflate_lat,inflate_lon:-inflate_lon]


input_bathy_amm15core_m_cs3xcs20 =  input_bathy_amm15core - cs3xcs20_bathy # we could probably make an expanded cs3x at least to the south, NW, NE not probably possible # NB. nemo interprets any point <= 0 as land (sets mbathy = 0)
# For now, convert any point <=0 to 1e-3, then land values = 0.
# Will need to consider changing this method when W&D comes in...

input_bathy_amm15core_m_cs3xcs20[ np.isnan( op_lsm_bath ) ] = np.nan  # Enfoce LSM as OP on core part of domain


# get coordinates of expanded domain

coord = Dataset((args.LAT_LON)[0],'r')
lat = coord.variables['gphit'][:,:]
lon = coord.variables['glamt'][:,:]

y,x = np.shape(lat)


# ====== write to file

ncfile = Dataset((args.OUT_FILE)[0],'w')
y_dim = ncfile.createDimension('x', x)     # Y
x_dim = ncfile.createDimension('y', y)     # X
latout = ncfile.createVariable('lat', 'f4', ('y','x',))
lonout = ncfile.createVariable('lon', 'f4', ('y','x',))
bathy = ncfile.createVariable('Bathymetry', 'f4', ('y','x',))

latout[:]=lat
lonout[:]=lon

Bath_hook = np.copy(input_bathy_amm15core_m_cs3xcs20)
Bath_hook[514:516,1106:1109] = 0



input_bathy[100:-100,100:-100] =  Bath_hook[:]
bathy[:] = input_bathy

ncfile.description = 'Expanded AMM15 bathymetry: Original source EMODNET data  converted from LAT to MSL [land mask=0].  Using CS3X and CS20'

now = datetime.now()
current_time = now.strftime("%Y/%m/%d %H:%M:%S")
repos = subprocess.run(['git', 'config', '--get', 'remote.origin.url'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
repos = repos.stdout.decode('utf-8').strip('\n')
branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref',  'HEAD'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
branch = branch.stdout.decode('utf-8').strip('\n')


script = parser.prog

ncfile.history = "Created by {} from branch {} of {} on {} ".format(script,branch[:],repos[:],current_time)
ncfile.inputs  = "{}, {}, {}, {}".format((args.OP_LSM)[0],(args.CS3X_CS20)[0],(args.BATHY_DATA)[0], (args.LAT_LON)[0] )
ncfile.pyversion = platform.python_version()
ncfile.System = platform.system()
ncfile.Release = platform.release()
import sys
ncfile.CommandLine = " ".join(sys.argv) # str(sys.argv)

latout.units = 'degrees north'
lonout.units = 'degrees east'
bathy.units = 'meters'

ncfile.close()


