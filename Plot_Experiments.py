import xarray as xr
import nc_time_axis
import matplotlib.pyplot as plt

models = ["UKESM1-0-LL", "IPSL-CM6A-LR", "MPI-ESM1-2-HR"] #IPSL-CM6A-LR, MPI-ESM1-2-HR, UKESM1-0-LL
scenarios = ["SSP126", "SSP370"]
experiments = ["noluc", "agtonat", "agtoaff", "nattoaff", "agtobio"]
colors = ["blue", "orange", "green", "red", "purple"]
line_styles = ["-", "--"]
markers = ["o", "s", "D"]

# Variables to loop over
#variables = ["TOTSOMC", "TOTSOMC_1m", "TOTVEGC", "TOTECOSYSC", "NBP", "GPP", "NPP", "TSA"]
#variables = ["NBP", "GPP", "NPP"]
variables = ["NBP"]

# Conversion factors
km2_to_m2 = 1e6
seconds_per_month = 365 * 24 * 60 * 60 / 12
k_to_degC = 273.15
g_to_Gt = 1e-15

# Create a figure and axis for each variable
for variable in variables:
    fig, ax = plt.subplots()
    print(variable)       

    for k, model in enumerate (models):
        for i, experiment in enumerate(experiments):
            for j, scenario in enumerate(scenarios):
                filename = f"/cluster/work/users/kjetisaa/PostProcessed_archive/{model}/{experiment}/ESM2025_{scenario}_{experiment}.nc"

                try:
                    data = xr.open_dataset(filename)

                    area = data["area"]
                    landfrac = data["landfrac"]
                    var_data = data[variable]
                    window_size = 10 * 12 #running mean (not for accumulated values)
                    # Convert variable data to appropriate units and multiply by area and landfrac
                    if  data[variable].units=="gC/m^2":
                        # Carbon pools: multiply by area and landfrac (convert m^2 to km^2)
                        var_total = (var_data * area * km2_to_m2 * landfrac * g_to_Gt).sum(dim=("lat", "lon"))
                        unit = f"GtC"
                    elif data[variable].units=="gC/m^2/s":
                        # Fluxes: multiply by area, landfrac, and seconds per year
                        var_total = (var_data * area * km2_to_m2 * landfrac * g_to_Gt * seconds_per_month).sum(dim=("lat", "lon")).cumsum(dim="time") 
                        unit = f"GtC"
                        window_size=12
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
                    # var_total_rolling.plot(ax=ax, label=f"{scenario} - {experiment}", color=colors[i], linestyle=line_styles[j], marker=markers[k])
                     var_total_rolling.plot(ax=ax, label=f"{scenario} - {experiment}", color=colors[i], linestyle=line_styles[j])

                except FileNotFoundError:
                    print(f"File not found for {experiment} - {scenario} - {model}. Skipping...")

    print(data[variable].units)
    print(unit)
    # Set the labels and title
    plt.xlabel("Time")
    plt.ylabel(f"Global Total {variable} ({unit})")
    plt.title(f"Running Mean (10-Year) Global Total {variable} Timeseries")

    # Add a legend
    plt.legend()

    # Save the plot as a PNG file
    plt.savefig(f"Figures/{variable}_timeseries.png")
