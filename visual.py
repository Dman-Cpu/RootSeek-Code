import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from scipy.signal import find_peaks

file_path = "RootDataset.csv"
df = pd.read_csv(file_path, skiprows=1, header=None, names=["time_us", "amplitude_mm"])

# Converting the cvs data
df["time_ms"] = df["time_us"] / 1000.0
df["amplitude_ft"] = df["amplitude_mm"] * 0.00328084

# Find high peaks
peaks, _ = find_peaks(df["amplitude_ft"], prominence=0.01)  # tweak prominence if needed
peak_amplitudes = df["amplitude_ft"].iloc[peaks]
peak_times = df["time_ms"].iloc[peaks]

# Highest and lowest peak
max_amp = peak_amplitudes.max()
min_amp = peak_amplitudes.min()
max_time = df["time_ms"].iloc[peak_amplitudes.idxmax()]
min_time = df["time_ms"].iloc[peak_amplitudes.idxmin()]

# Use histogram to find most common peak amplitude range
hist, bin_edges = np.histogram(peak_amplitudes, bins=20)
most_common_bin = np.argmax(hist)
range_start = bin_edges[most_common_bin]
range_end = bin_edges[most_common_bin + 1]

# Show popup with peak analysis results
root = tk.Tk()
root.withdraw()
message = f"""Root Signal Peak Analysis:

- Highest peak: {max_amp:.2f} ft at {max_time:.2f} ms
- Lowest peak: {min_amp:.2f} ft at {min_time:.2f} ms
- Most probable root depth range (based on high peaks):
  {range_start:.2f} ft to {range_end:.2f} ft
"""
messagebox.showinfo("Root Detection (Peak-Based)", message)

# Plot signal with peaks and probable root range
plt.figure(figsize=(10, 6))
plt.plot(df["time_ms"], df["amplitude_ft"], label="Amplitude (ft)", color='teal')
plt.scatter(peak_times, peak_amplitudes, color='orange', label='Detected Peaks', s=30)
plt.axhline(y=range_start, color='gray', linestyle='--', label="Most Probable Range")
plt.axhline(y=range_end, color='gray', linestyle='--')
plt.scatter([max_time], [max_amp], color='red', label="Highest Peak", zorder=5)
plt.scatter([min_time], [min_amp], color='blue', label="Lowest Peak", zorder=5)
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude (feet)")
plt.title("Signal Amplitude & Root Depth Analysis (Peak-Based)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
