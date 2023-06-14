import xarray as xr
import nc_time_axis
import matplotlib.pyplot as plt

experiments = ["noluc", "agtonat", "agtoaff", "nattoaff", "agtobio"]
colors = ["blue", "orange", "green", "red", "purple"]

# Time periods for map plotting
time_periods = [("2040-01-01", "2050-12-31"), ("2090-01-01", "2100-12-31")]

# Conversion factors
km2_to_m2 = 1e6
g_to_Gt = 1e-15
for i, experiment in enumerate(experiments):
    print(experiment)
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
    
    for j, time_period in enumerate(time_periods):

        filename = f"/cluster/work/users/kjetisaa/PostProcessed_archive/UKESM1-0-LL/{experiment}/ESM2025_SSP126_{experiment}.nc"
        data = xr.open_dataset(filename)
        
        area = data["area"]
        landfrac = data["landfrac"]
        nbp_data = data["NBP"]
        
        # Select the time period and average over time
        nbp_period = nbp_data.sel(time=slice(*time_period)).mean(dim="time")
        
        # Multiply by area, landfrac, and conversion factor
        nbp_total = (nbp_period)
        
        # Plot the map
        ax = axs[j]
        print(j)
        nbp_total.plot(ax=ax, cmap="coolwarm")
        ax.set_title(f"NBP - {experiment} - {time_period}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
    # Adjust layout and save the figure
    plt.tight_layout()
    plt.savefig(f"Figures/SSP126_NBP_map_{experiment}.png")
    plt.close()
