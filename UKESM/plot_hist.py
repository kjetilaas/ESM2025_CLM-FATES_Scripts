import xarray as xr
import matplotlib.pyplot as plt

# Define the absolute path to the directory containing your netCDF files
#directory_path = "/cluster/work/users/kjetisaa/archive/ESM2025_UKESM1-0-LL_BGC-CROP_HIST_f19_g17_historical/lnd/hist"
# Define the file pattern of your netCDF files
#file_pattern = "ESM2025_UKESM1-0-LL_BGC-CROP_HIST_f19_g17_historical.clm2.h0.*.nc"  # Replace "file_prefix" with the common prefix of your files
# Construct the file paths using the directory path and file pattern
#file_paths = f"{directory_path}/{file_pattern}"
# Load data from the netCDF files
#data = xr.open_mfdataset(file_paths, chunks={'time': 100})

filename="/cluster/work/users/kjetisaa/Temp_archive/UKESM/TOTSOMC_hist.nc" #Produced with "cdo -O -mergetime -apply,-selvar,TOTSOMC,area [ infiles*.nc ] outfile.nc"
data = xr.open_dataset(filename)


area = data["area"]  # Assuming the 2D variable is named "area"
totsomc = data["TOTSOMC"]  # Assuming the variable is named "TOTSOMC"

# Multiply TOTSOMC with area to get global total soil organic carbon
global_totsomc = (totsomc * area).sum(dim=("lat", "lon"))
print(global_totsomc.shape)
# Plot the timeseries
global_totsomc.plot()
plt.xlabel("Time")
plt.ylabel("Global Total Soil Organic Carbon")
plt.title("Monthly Mean Global Total Soil Organic Carbon Timeseries")

# Save the plot as a PNG file
plt.savefig("TOTSOMC_timeseries.png") 
