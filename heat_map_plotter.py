import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.ndimage import zoom
from multiprocessing import Array
import struct


# Function to update heatmap based on the shared array
def update_heatmap(frame, shared_array, heatmap):
    # Read the shared array and convert it into a 2D matrix
    matrix_data = np.frombuffer(shared_array.get_obj(), dtype=np.float32).reshape(8, 8)

    # Interpolate the 8x8 matrix to 16x16 using scipy's zoom function
    interpolated_data = zoom(matrix_data, (2, 2), order=1)  # order=1 is bilinear interpolation

    # Clip the values to ensure the max value is capped at 2000
    clipped_data = np.clip(interpolated_data, 0, 2000)

    # Update the heatmap data with the clipped data
    heatmap.set_data(clipped_data)

    # Trigger a redraw of the heatmap
    plt.draw()

    return [heatmap]

# Function to create the heatmap and start animation
def create_heatmap(shared_array):
    # Initialize figure for plotting
    fig, ax = plt.subplots()

    # Create a placeholder for the heatmap, setting vmin and vmax to control the range of values
    heatmap = ax.imshow(np.zeros((8, 8)), cmap='gist_ncar', interpolation='nearest', vmin=0, vmax=2000)
    plt.colorbar(heatmap, ax=ax)

    # Create the animation (set interval to a positive value)
    ani = FuncAnimation(fig, update_heatmap, fargs=(shared_array, heatmap), interval=1, cache_frame_data=False)  # Update every 100ms

    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Create a shared array (8x8 matrix flattened into a 1D array of 64 floats)
    shared_array = Array('f', 64)  # 64 floats for an 8x8 m,atrix

    # Start the serial reader in a separate thread
    from proto_1 import start_serial_reader
    serial_thread = start_serial_reader(shared_array)

    # Start the heatmap display
    create_heatmap(shared_array)

    # Keep the process running
    serial_thread.join()
