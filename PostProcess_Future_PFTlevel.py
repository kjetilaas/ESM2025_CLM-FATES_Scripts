import netCDF4 as nc
import numpy as np
import glob
import os.path

#Script to post process ESM2025 simulations on PFT level. 
#Based on Daniel's scrip: https://github.com/djk2120/ctsm_trendy_2022/blob/master/post/make_gcp2022_bypft_output_files.py
#Requires CLM output to be merged to one file pr variable (with "PostProcess_ESM2025_pftlevel.sh")

models = ["UKESM1-0-LL", "IPSL-CM6A-LR", "MPI-ESM1-2-HR"] 
scenarios = ["SSP126", "SSP370"] 
experiments = ["noluc", "agtonat", "agtoaff", "nattoaff", "agtobio", "nattobio"]
vars_in = ['TLAI', 'FCTR', 'TOTVEGC', 'GPP', 'NPP', 'TV', 'HTOP'] #, 'NBP'

#models = ["UKESM1-0-LL"] #IPSL-CM6A-LR, MPI-ESM1-2-HR, UKESM1-0-LL
#scenarios = ["SSP126"] #"SSP126",
#experiments = ["noluc"]
#vars_in = ['TLAI', 'FCTR', 'TOTVEGC', 'GPP', 'NPP', 'TV', 'HTOP']

d='/cluster/work/users/kjetisaa/PostProcessed_archive/Temp_results_PFTlevel/'
datadir_out = '/cluster/work/users/kjetisaa/PostProcessed_archive/ESM2025_WP10_postprocessed_pftlevel/'

vars_out = ['mrso', 'mrro', 'evapotrans', 'sh', 'Ts', 'cVeg', 'cLitter', 'cSoil', 'gpp', 'ra', 'npp', 'rh', 'fFire', 'fLuc', 'nbp', 'landCoverFrac', 'lai', 'tsl', 'msl', 'evspsblveg', 'evspsblsoi', 'tran', 'swup', 'lwup', 'ghflx', 'snow_depth', 'swe', 'fGrazing', 'fHarvest', 'fVegLitter', 'fLitterSoil', 'fVegSoil', 'cLeaf', 'cWood', 'cRoot', 'cCwd', 'burntArea', 'cProduct', 'dlai', 'evapotranspft', 'transpft', 'evapo', 'cVegpft', 'gpppft', 'npppft','nbppft','tskinpft','irripft']
units_out_list = ['kg m-2', 'kg m-2 s-1', 'kg m-2 s-1', 'W m-2', 'K', 'kg m-2', 'kg m-2', 'kg m-2', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'None', 'None', 'K', 'kg m-2', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'W m-2', 'W m-2', 'W m-2', 'm', 'kg m-2', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2', 'kg m-2', 'kg m-2', 'kg m-2', '%', 'kg m-2', 'None', 'W m-2','W m-2','W m-2','kg m-2', 'kg m-2 s-1', 'kg m-2 s-1', 'kg m-2 s-1', 'K', 'kg m-2 s-1']
long_name_out_list = ['Total Soil Moisture Content', 'Total Runoff', 'Total Evapo-Transpiration', 'Sensible heat flux', 'Surface temperature', 'Carbon in Vegetation', 'Carbon in Above-ground Litter Pool', 'Carbon in Soil (including below-ground litter)', 'Gross Primary Production', 'Autotrophic (Plant) Respiration', 'Net Primary Production', 'Heterotrophic Respiration', 'CO2 Emission from Fire', 'CO2 Flux to Atmosphere from Land Use Change', 'Net Biospheric Production', 'Fractional Land Cover of PFT', 'Leaf Area Index', 'Temperature of Soil', 'Moisture of Soil', 'Evaporation from Canopy', 'Water Evaporation from Soil', 'Transpiration', 'Shortwave up radiation', 'Longwave up radiation', 'Ground heat flux', 'Snow Depth ', 'Snow Water Equivalent ', 'CO2 Flux to Atmosphere from Grazing', 'CO2 Flux to Atmosphere from Crop Harvesting', 'Total Carbon Flux from Vegetation to Litter', 'Total Carbon Flux from Litter to Soil', 'Total Carbon Flux from Vegetation Directly to Soil', 'Carbon in Leaves', 'Carbon in Wood', 'Carbon in Roots', 'Carbon in Coarse Woody Debris', 'Burnt Area Fraction', 'Carbon in Products of Land Use Change', 'Leaf Area Index Daily', 'Vegtype level evapotranspiration', 'Vegtype level transpiration','Vegtype level Soil evaporation','Vegtype level Carbon in Vegetation','Vegtype level GPP','Vegtype level NPP','Vegtype level NBP','Vegtype level Skin temperature','Vegtype level irrigation']

def clobber(filename):
    try:
        print('replacing file: '+filename)
        os.remove(filename)
    except:
        print('file does not exist: '+filename)

def separate_clmhist_bypft(file_in, variable_name=None, IM=None, JM=None, npft=None, verbose = True, pftcoords_file=None):
    """function to separate 1-D or 2_D vector of data into 3-D or 4-D array.  IM is the number of longitude gridpoints, JM is the number of latitude gridpoints, and npft is the number of PFTs."""

    #
    if pftcoords_file == None:
        pftcoords_file = file_in
        #
    pftvars = []
    for variable in file_in.variables:
        dims = file_in.variables[variable].dimensions
        if 'pft' in dims:
            pftvars.append(variable)
            #
    if not variable_name in pftvars:
        if variable_name == None:
            return pftvars
        else:
            print('variable '+variable_name+ ' not in pft variable list.')
            print(pftvars)
            raise RuntimeError
        #
    if IM==None:
        IM = np.max(pftcoords_file.variables['pfts1d_ixy'])
    if JM==None:
        JM = np.max(pftcoords_file.variables['pfts1d_jxy'])
    if npft==None:
        npft = np.max(pftcoords_file.variables['pfts1d_itype_veg'])+1 ## zero is valid pft
        #
    vardims = list(file_in.variables[variable_name].dimensions)
    ndims_in_wo_pft = len(vardims)-1
    ndims_out = ndims_in_wo_pft+3
    vardims.append('lat')
    vardims.append('lon')    
    dims_out_size = [file_in.dimensions['time'].size,npft,JM,IM]
    badno = file_in.variables[variable_name].missing_value

    #
    if ndims_in_wo_pft == 1:
        data_out = np.ma.masked_all(dims_out_size)
        for pft in range(npft):
            print(' running pft '+str(pft) + ' of '+str(npft))
            var_in = file_in.variables[variable_name]
            ### now loop over timesteps
            pftlonindices = np.extract(np.logical_and(pftcoords_file.variables['pfts1d_itype_veg'][:] == pft, var_in[0,:] < badno), pftcoords_file.variables['pfts1d_ixy'][:]) -1
            pftlatindices = np.extract(np.logical_and(pftcoords_file.variables['pfts1d_itype_veg'][:] == pft, var_in[0,:] < badno), pftcoords_file.variables['pfts1d_jxy'][:]) -1
            for i in range(dims_out_size[0]):
                # if i%10 == 0:
                #     print(' running pft '+str(i) + ' of '+str(dims_out_size[0]))
                varpft = np.extract(np.logical_and(pftcoords_file.variables['pfts1d_itype_veg'][:] == pft, var_in[0,:] < badno), var_in[i,:])
                varpftindices = pftlonindices + pftlatindices*IM + pft*IM*JM + i*npft*IM*JM
                data_out.flat[varpftindices] = varpft
                #
    elif ndims_in_wo_pft == 0:
        data_out = np.ma.masked_all(dims_out_size)
        for pft in range(npft):
            var_in = file_in.variables[variable_name]
            ### now loop over timesteps
            varpft = np.extract(np.logical_and(pftcoords_file.variables['pfts1d_itype_veg'][:] == pft, var_in[:] < badno), var_in[:])
            pftlonindices = np.extract(np.logical_and(pftcoords_file.variables['pfts1d_itype_veg'][:] == pft, var_in[:] < badno), pftcoords_file.variables['pfts1d_ixy'][:]) -1
            pftlatindices = np.extract(np.logical_and(pftcoords_file.variables['pfts1d_itype_veg'][:] == pft, var_in[:] < badno), pftcoords_file.variables['pfts1d_jxy'][:]) -1
            varpftindices = pftlonindices + pftlatindices*IM + pft*IM*JM 
            data_out.flat[varpftindices]= varpft
            #
    else:
        raise NotImplementedError
    #
    return data_out

def write_outfile(data_out, filename_out, varname_out):                               
            clobber(filename_out)
            file_out = nc.Dataset(filename_out, 'w', format='NETCDF4')
            file_out.createDimension('lat', JM)
            file_out.createDimension('lon', IM)
            file_out.createDimension('pft', npft)
            file_out.createDimension('time', ntime_monthly)
            file_out.createDimension('bnds', 2)
            file_latvarout = file_out.createVariable('lat', 'f4', ('lat',))
            file_lonvarout = file_out.createVariable('lon', 'f4', ('lon',))
            file_timevarout = file_out.createVariable('time', 'f4', ('time',))
            file_timebndsvarout = file_out.createVariable('time_bnds', 'f4', ('time','bnds',))
            file_latvarout[:] = lats[:]
            file_lonvarout[:] = lons[:]
            file_timevarout[:] = time[:]
            file_timebndsvarout[:,:] = time_bnds[:,:]
            file_latvarout.units = lats.units
            file_lonvarout.units = lons.units
            file_timevarout.units=time.units
            file_timevarout.bounds=time.bounds
            for pft_i in range(npft):
                setattr(file_out,'pft_name_'+"%02d" % (pft_i),pftname[pft_i])

            varname_out_ext = varname_out
            file_varout = file_out.createVariable(varname_out_ext, 'f4', ('time', 'pft', 'lat', 'lon'))
            file_varout[:] = data_out[:, :, :, :].astype('float32')     
            file_varout.units=units_out_list[list_index]
            file_varout.Long_name=long_name_out_list[list_index]
            file_varout.unit_conversion_factor=unit_conversion
            file_varout.CLM_orig_varname=varname_in

            file_out.close()            

pftname =   ["not_vegetated", 
             "needleleaf_evergreen_temperate_tree", 
             "needleleaf_evergreen_boreal_tree", 
             "needleleaf_deciduous_boreal_tree", 
             "broadleaf_evergreen_tropical_tree", 
             "broadleaf_evergreen_temperate_tree", 
             "broadleaf_deciduous_tropical_tree", 
             "broadleaf_deciduous_temperate_tree", 
             "broadleaf_deciduous_boreal_tree", 
             "broadleaf_evergreen_shrub", 
             "broadleaf_deciduous_temperate_shrub", 
             "broadleaf_deciduous_boreal_shrub", 
             "c3_arctic_grass", 
             "c3_non-arctic_grass", 
             "c4_grass", 
             "unmanaged_c3_crop", 
             "unmanaged_c3_irrigated", 
             "corn", 
             "irrigated_corn", 
             "spring_wheat", 
             "irrigated_spring_wheat", 
             "winter_wheat", 
             "irrigated_winter_wheat", 
             "soybean", 
             "irrigated_soybean",
             "barley",
             "irrigated_barley",
             "winter_barley",
             "irrigated_winter_barley",
             "rye",
             "irrigated_rye",
             "winter_rye",
             "irrigated_winter_rye",
             "cassava",
             "irrigated_cassava",
             "citrus",
             "irrigated_citrus",
             "cocoa",
             "irrigated_cocoa",
             "coffee",
             "irrigated_coffee",
             "cotton",
             "irrigated_cotton",
             "datepalm",
             "irrigated_datepalm",
             "foddergrass",
             "irrigated_foddergrass",
             "grapes",
             "irrigated_grapes",
             "groundnuts",
             "irrigated_groundnuts",
             "millet",
             "irrigated_millet",
             "oilpalm",
             "irrigated_oilpalm",
             "potatoes",
             "irrigated_potatoes",
             "pulses",
             "irrigated_pulses",
             "rapeseed",
             "irrigated_rapeseed",
             "rice",
             "irrigated_rice",
             "sorghum",
             "irrigated_sorghum",
             "sugarbeet",
             "irrigated_sugarbeet",
             "sugarcane",
             "irrigated_sugarcane",
             "sunflower",
             "irrigated_sunflower",
             "miscanthus",
             "irrigated_miscanthus",
             "switchgrass",
             "irrigated_switchgrass",
             "tropical_corn",
             "irrigated_tropical_corn",
             "tropical_soybean",
             "irrigated_tropical_soybean"]


npft = 79


#experiment='noluc'
#model='UKESM1-0-LL'
#scenario='SSP126'

for k, model in enumerate (models):
    print('starting model '+model)
    for i, experiment in enumerate(experiments):
        print('starting experiment '+experiment)
        for j, scenario in enumerate(scenarios):
            print('starting scenario '+scenario)
            coord_read = False

            dcoord='/cluster/work/users/kjetisaa/archive/ESM2025_'+model+'_BGC-CROP_'+scenario+'_f19_g17_'+experiment+'/lnd/hist/'
            fnamecoord='ESM2025_'+model+'_BGC-CROP_'+scenario+'_f19_g17_'+experiment+'.clm2.h1.2100-12.nc'
            
            pftcoords_file = nc.Dataset(dcoord+fnamecoord)

            for var_i, varname in enumerate(vars_in):
                print('starting var '+varname)
                locals()[varname] = None
                #
                fname='clm_'+model.lower()+'_'+scenario.lower()+'_'+experiment+'_'+varname+'.monthly.h1_RAW.nc'

                filename=d+fname 
                if os.path.isfile(filename):
                    filein=nc.Dataset(filename)        
                    #
                    if coord_read:
                        print('Coordinates already read')
                    else:
                        print('Reading coodinates')                        
                        lats = pftcoords_file.variables['lat']
                        lons = pftcoords_file.variables['lon']
                        time = filein.variables['time']
                        time_bnds = filein.variables['time_bnds']
                        ntime_monthly = len(time[:])
                        ntime_annual = ntime_monthly / 12
                        JM = len(lats[:])
                        IM = len(lons[:])
                        coord_read = True
                    locals()[varname] = separate_clmhist_bypft(filein, variable_name=varname, IM=IM, JM=JM, npft=npft, pftcoords_file=pftcoords_file)
                    #
                else:
                    print("File not read:"+filename)
            

            exp_outputname = 'clm_'+model.lower()+ '_' +scenario.lower()+ '_' +experiment+'_'


            #Write new PFT level files. Should be rewritten to not duplicate code...

            #############   lai   #############
            varname_out = 'lai'
            varname_in = 'TLAI'
            unit_conversion = 1.
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'              
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1
            
            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)                                  
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)

            #############   cVegpft   #############
            varname_out = 'cVegpft'
            varname_in = 'TOTVEGC'
            unit_conversion = 1.e-3
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'                          
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1

            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)                    
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)

            #############   transpft   #############
            varname_out = 'transpft'
            varname_in = 'FCTR'
            unit_conversion = 1.
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'                          
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1            

            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)          
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)

            #############   gpppft   #############
            varname_out = 'gpppft'
            varname_in = 'GPP'
            unit_conversion = 1.e-3
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'                          
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1

            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)                   
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)

            #############   npppft   #############
            varname_out = 'npppft'
            varname_in = 'NPP'
            unit_conversion = 1.e-3
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'                          
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1

            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)                    
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)

            #############   nbppft   #############
            #---Not a PFT level variable---
            varname_out = 'nbppft'
            varname_in = 'NBP'
            unit_conversion = 1.e-3
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'                          
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1
            
            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)                    
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)

            #############   tskinpft   #############
            varname_out = 'tskinpft'
            varname_in = 'TV'
            unit_conversion = 1.
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'                          
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1

            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)                   
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)

            #############   theightpft   #############
            varname_out = 'theightpft'
            varname_in = 'HTOP'
            unit_conversion = 1.
            filename_out = datadir_out + exp_outputname + varname_out +'.monthly.nc'                          
            try:
                list_index = vars_out.index(varname_out)
            except:
                list_index = -1

            try:
                data_out = locals()[varname_in][:,:,:,:] * unit_conversion
                np.ma.set_fill_value(data_out, -99999.)                    
                write_outfile(data_out=data_out, filename_out=filename_out, varname_out=varname_out)             
                del data_out
            except:
                print("File not written:"+filename_out)             