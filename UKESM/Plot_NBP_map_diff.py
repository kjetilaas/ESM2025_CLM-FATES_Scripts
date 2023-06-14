import xarray as xr
import nc_time_axis
import matplotlib.pyplot as plt

experiments = ["agtonat", "agtoaff", "nattoaff", "agtobio"]
colors = ["blue", "orange", "green", "red", "purple"]

# Time periods for map plotting
time_periods = [("2040-01-01", "2050-12-31"), ("2090-01-01", "2100-12-31")]

# Conversion factors
km2_to_m2 = 1e6
g_to_Gt = 1e-15

ref_experiment = "noluc"  # Reference experiment

for i, experiment in enumerate(experiments):
    print(experiment)
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
    
    for j, time_period in enumerate(time_periods):

        filename_ref = f"/cluster/work/users/kjetisaa/PostProcessed_archive/UKESM1-0-LL/{ref_experiment}/ESM2025_SSP126_{ref_experiment}.nc"
        filename_exp = f"/cluster/work/users/kjetisaa/PostProcessed_archive/UKESM1-0-LL/{experiment}/ESM2025_SSP126_{experiment}.nc"
        data_ref = xr.open_dataset(filename_ref)
        data_exp = xr.open_dataset(filename_exp)
        
        area = data_ref["area"]
        landfrac = data_ref["landfrac"]
        nbp_data_ref = data_ref["NBP"]
        nbp_data_exp = data_exp["NBP"]
        
        # Select the time period and average over time
        nbp_period_ref = nbp_data_ref.sel(time=slice(*time_period)).mean(dim="time")
        nbp_period_exp = nbp_data_exp.sel(time=slice(*time_period)).mean(dim="time")
        
        # Calculate the difference between experiment and reference
        nbp_diff = nbp_period_exp - nbp_period_ref
        
        # Multiply by area, landfrac, and conversion factor
        nbp_total = nbp_diff * area * landfrac * km2_to_m2 * g_to_Gt
        
        # Plot the map
        ax = axs[j]
        nbp_total.plot(ax=ax, cmap="coolwarm")
        ax.set_title(f"NBP - {experiment} - {time_period}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
    
    # Adjust layout and save the figure
    plt.tight_layout()
    plt.suptitle(f"Difference in NBP ({experiment} - {ref_experiment})", fontsize=16)
    plt.savefig(f"Figures/SSP126_NBP_map_Diff_{experiment}.png", dpi=300)
    plt.close()
