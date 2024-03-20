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


# theta is the direction of interest, in radians, and r is our received signal
def w_mvdr(theta, r, d, Nr):
   a = np.exp(-2j * np.pi * d * np.arange(Nr) * np.sin(theta)) # steering vector in the desired direction theta
   a = a.reshape(-1,1) # make into a column vector (size 3x1)
   R = r @ r.conj().T # Calc covariance matrix. gives a Nr x Nr covariance matrix of the samples
   Rinv = np.linalg.pinv(R) # 3x3. pseudo-inverse tends to work better/faster than a true inverse
   w = (Rinv @ a)/(a.conj().T @ Rinv @ a) # MVDR/Capon equation! numerator is 3x3 * 3x1, denominator is 1x3 * 3x3 * 3x1, resulting in a 3x1 weights vector
   return w


sdr = ADI()

freq = int(3e9)

sdr.set_rf_frequency(freq)

sdr.set_samplerate(30e6)

array_element_distance = 0.04996540966

ula = arrays.UniformLinearArray(m=4, dd=array_element_distance)

print(ula.steering_vector)

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


    w = w_mvdr(angles[0], data, d=array_element_distance, Nr=4)


    data_weighted = w.conj().T @ data


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