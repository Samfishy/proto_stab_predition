import serial
import numpy as np
from multiprocessing import Process, Array
import threading

# Open serial port (adjust the port and baud rate as per your setup)
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # Change to the correct port

# Function to read and process the serial data
def read_serial_data(shared_array):
    data_buffer = ""

    while True:
        # Read incoming data from the serial port (byte-by-byte)
        raw_data = ser.readline().decode('utf-8').strip()

        if raw_data:
            data_buffer += raw_data

            # Debugging: Print raw data
            # print(f"Raw data received: {raw_data}")

            # Check if the data buffer contains a complete 8x8 matrix (starts with '[[' and ends with ']]')
            if '[[' in data_buffer and ']]' in data_buffer:
                while '[[' in data_buffer and ']]' in data_buffer:
                    # Extract the first complete matrix from the buffer
                    start_index = data_buffer.index('[[')
                    end_index = data_buffer.index(']]') + 2

                    matrix_str = data_buffer[start_index:end_index]
                    data_buffer = data_buffer[end_index:]

                    try:
                        # Remove the outer brackets and split the matrix
                        matrix_str = matrix_str[2:-2]  # Strip the '[[' and ']]'
                        rows = matrix_str.split('],[')
                        parsed_data = np.array([list(map(int, row.split(','))) for row in rows])

                        # Ensure it's an 8x8 matrix
                        if parsed_data.shape == (8, 8):
                            # Write to the shared array (flattened to 1D)
                            shared_array[:] = parsed_data.flatten()

                            # Debugging: Print the matrix
                            # print("Matrix stored in shared array:")
                            # print(parsed_data)
                    except ValueError as e:
                        # If there's a parsing issue, reset the buffer
                        # print(f"Error parsing matrix: {e}, skipping.")
                        data_buffer = ""  # Reset the buffer

# Function to start the serial data reader in a separate process
def start_serial_reader(shared_array):
    serial_thread = threading.Thread(target=read_serial_data, args=(shared_array,))
    serial_thread.daemon = True  # Allow this thread to exit when the main program exits
    serial_thread.start()
    return serial_thread

if __name__ == "__main__":
    # Create a shared array (8x8 matrix flattened into a 1D array of 64 floats)
    shared_array = Array('f', 64)  # 64 floats for an 8x8 matrix

    # Start the serial data reader in a separate thread
    serial_thread = start_serial_reader(shared_array)

    # Keep the process running
    serial_thread.join()
