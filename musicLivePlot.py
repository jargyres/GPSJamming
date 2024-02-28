from ADI import ADI
import time
import numpy as np
import ctypes
from classical_doa import arrays, signals
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from classical_doa.algorithm.music import music
from scipy.signal import find_peaks

def plot_spatial_spectrum(spectrum, ground_truth, angle_grids,
                          peak_threshold=0.5, x_label="Angle",
                          y_label="Spectrum"):
    """Plot spatial spectrum

    Args:
        spectrum: Spatial spectrum estimated by the algorithm
        ground_truth: True incident angles
        angle_grids: Angle grids corresponding to the spatial spectrum
        peak_threshold: Threshold used to find peaks in normalized spectrum
        x_label: x-axis label
        y_label: y-axis label
    """
    spectrum = spectrum / np.max(spectrum)
    # find peaks and peak heights
    peaks_idx, heights = find_peaks(spectrum,
                                    height=peak_threshold)
    angles = angle_grids[peaks_idx]
    heights = heights["peak_heights"]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # set ticks
    grids_min = angle_grids[0]
    grids_max = angle_grids[-1]
    major_space = (grids_max - grids_min + 1) / 6
    minor_space = major_space / 5
    ax.set_xlim(grids_min, grids_max)
    ax.xaxis.set_major_locator(plt.MultipleLocator(major_space))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(minor_space))

    # plot spectrum
    ax.plot(angle_grids, spectrum)
    ax.set_yscale('log')

    # plot peaks
    ax.scatter(angles, heights, color="red", marker="x")
    for i, angle in enumerate(angles):
        ax.annotate(angle, xy=(angle, heights[i]))

    # ground truth
    for angle in ground_truth:
        ax.axvline(x=angle, color="green", linestyle="--")

    # set labels
    ax.legend(["Spectrum", "Estimated", "Ground Truth"])

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    plt.show()


sdr = ADI()

freq = int(3e9)

sdr.set_rf_frequency(freq)

sdr.set_samplerate(30e6)

ula = arrays.UniformLinearArray(m=4, dd=0.062)

angle_grids = np.arange(-90, 90, 1)

peak_threshold = 0.5

x_label="Angle",

y_label="Spectrum"

data = np.asarray(sdr.sdr.rx())

spectrum = music(received_data=data, num_signal=1, array=ula, signal_fre=freq, angle_grids=angle_grids, unit='deg')

fig = plt.figure("Direction of Arrival Estimation")

ax = fig.add_subplot()

spectrum = spectrum / np.max(spectrum)
# find peaks and peak heights
peaks_idx, heights = find_peaks(spectrum,
                                height=peak_threshold)
angles = angle_grids[peaks_idx]
heights = heights["peak_heights"]

# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)

# set ticks
grids_min = angle_grids[0]
grids_max = angle_grids[-1]
major_space = (grids_max - grids_min + 1) / 6
minor_space = major_space / 5
ax.set_xlim(grids_min, grids_max)
ax.xaxis.set_major_locator(plt.MultipleLocator(major_space))
ax.xaxis.set_minor_locator(plt.MultipleLocator(minor_space))

# plot spectrum
ax.clear()
ax.relim()
ax.plot(angle_grids, spectrum)
ax.set_yscale('log')

# plot peaks
ax.scatter(angles, heights, color="red", marker="x")
for i, angle in enumerate(angles):
    ax.annotate(angle, xy=(angle, heights[i]))

# ground truth
ground_truth=np.array([0])
for angle in ground_truth:
    ax.axvline(x=angle, color="green", linestyle="--")

# set labels
ax.legend(["Spectrum", "Estimated", "Ground Truth"])

ax.set_xlabel(x_label)
ax.set_ylabel(y_label)


def update(i):

    data = np.asarray(sdr.sdr.rx())

    spectrum = music(received_data=data, num_signal=1, array=ula, signal_fre=freq, angle_grids=angle_grids, unit='deg')

    ax.clear()

    spectrum = spectrum / np.max(spectrum)
    # find peaks and peak heights
    peaks_idx, heights = find_peaks(spectrum,
                                    height=peak_threshold)
    angles = angle_grids[peaks_idx]
    heights = heights["peak_heights"]

    # set ticks
    grids_min = angle_grids[0]
    grids_max = angle_grids[-1]
    major_space = (grids_max - grids_min + 1) / 6
    minor_space = major_space / 5
    ax.set_xlim(grids_min, grids_max)
    ax.xaxis.set_major_locator(plt.MultipleLocator(major_space))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(minor_space))

    # plot spectrum
    ax.plot(angle_grids, spectrum)
    ax.set_yscale('log')

    # plot peaks
    ax.scatter(angles, heights, color="red", marker="x")
    for i, angle in enumerate(angles):
        ax.annotate(angle, xy=(angle, heights[i]))

    # ground truth
    ground_truth=np.array([0])
    for angle in ground_truth:
        ax.axvline(x=angle, color="green", linestyle="--")


ani = animation.FuncAnimation(fig, update, interval=50)


plt.show()