import xarray as xr
import nc_time_axis
import matplotlib.pyplot as plt


filename="/cluster/work/users/kjetisaa/PostProcessed_archive/UKESM1-0-LL/ESM2025_HISTORICAL.nc" #Produced with "cdo -O -mergetime -apply,-selvar,TOTSOMC,area [ infiles*.nc ] outfile.nc"
data = xr.open_dataset(filename)

# Variables to loop over
variables = ["TOTSOMC", "TOTSOMC_1m", "TOTVEGC", "TOTECOSYSC", "NBP", "GPP", "NPP", "TSA"]

# Window size for running mean (in months)
window_size = 10 * 12

# Conversion factors
km2_to_m2 = 1e6
seconds_per_year = 365 * 24 * 60 * 60
k_to_degC = 273.15
g_to_Gt = 1e-15

# Create a figure and axis for each variable
for variable in variables:
    fig, ax = plt.subplots()
    print(variable)

    area = data["area"]  # Assuming the 2D variable is named "area"
    landfrac = data["landfrac"]
    var_data = data[variable]  # Assuming the variable is named "TOTSOMC"

    # Convert variable data to appropriate units and multiply by area and landfrac
    if  data[variable].units=="gC/m^2":
        # Carbon pools: multiply by area and landfrac (convert m^2 to km^2)
        var_total = (var_data * area * km2_to_m2 * landfrac * g_to_Gt).sum(dim=("lat", "lon"))
        unit = f"GtC"
    elif data[variable].units=="gC/m^2/s":
        # Fluxes: multiply by area, landfrac, and seconds per year
        var_total = (var_data * area * km2_to_m2 * landfrac * g_to_Gt * seconds_per_year).sum(dim=("lat", "lon"))
        unit = f"GtC/yr"
    elif data[variable].units=="K":
        # Temperature: convert to global, area-weighted mean (no conversion to C as it's already in K)
        var_total = (var_data * area * landfrac).sum(dim=("lat", "lon")) / (area * landfrac ).sum(dim=("lat", "lon"))
        unit = data[variable].units
    else:
        var_total = var_data
        unit = data[variable].units

    # Calculate running mean
    var_total_rolling = var_total.rolling(time=window_size, center=True).mean()

    # Plot the timeseries with the corresponding color and label
    var_total_rolling.plot()

    # Set the labels and title
    plt.xlabel("Time")
    plt.ylabel(f"Global Total {variable} ({unit})")
    plt.title(f"Running Mean (10-Year) Global Total {variable} Timeseries")

    # Save the plot as a PNG file
    plt.savefig(f"Figures/HISTORICAL_{variable}_timeseries.png") 
