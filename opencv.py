import cv2
import cvzone
from cvzone.FaceDetectionModule import FaceDetector
from ultralytics import YOLO
import supervision as sv
import numpy as np
import serial

# Define the polygon zone for the face detection area
ZONE_POLYGON = np.array([
    [360, 200],
    [280, 200],
    [280, 280],
    [360, 280]
])

# Serial communication setup
serial_port = "/dev/ttyUSB0"  # Adjust this to your serial port
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate, timeout=1)  # Open serial port

def send_position_to_serial(cell_number):
    """
    Send the grid cell number where the face is detected to the serial port.
    """
    if ser.is_open:
        try:
            ser.write(f"{cell_number}\n".encode())  # Send cell number as string followed by a newline
            print(f"Sent position: {cell_number} to serial port")
        except Exception as e:
            print(f"Error sending position to serial: {e}")

def main():
    # Initialize video capture (camera)
    cap = cv2.VideoCapture(0)  # Update the index if necessary

    # Set the resolution of the video capture to 640x480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the width of the frame
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the height of the frame

    # Load YOLOv8 model
    model = YOLO("yolov8l.pt")
    model.to('cuda')

    # Face detector
    detector = FaceDetector(minDetectionCon=0.5, modelSelection=0)

    # Create a random matrix for visualization (can replace with actual data if needed)
    matrix = np.random.randint(0, 256, (16, 16))  # 16x16 grid matrix
    cell_width = 640 // 16  # Adjusted to 16 cells horizontally
    cell_height = 480 // 16  # Adjusted to 16 cells vertically

    # Box annotator for object detections
    box_an = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    while True:
        # Read the frame from the camera
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to read frame.")
            break

        # Flip the frame horizontally (mirror the image)
        frame = cv2.flip(frame, 1)  # 1 means flip horizontally

        # Detect faces using the cvzone FaceDetector
        frame, bboxs = detector.findFaces(frame, draw=False)

        # Perform object detection with YOLO
        results = model(frame, agnostic_nms=True, conf=0.50)[0]
        detections = sv.Detections.from_yolov8(results)

        pos_bx_x, pos_bx_y = None, None  # Position of face in the grid
        green_cell_number = None  # Store the grid cell number for the green dot

        if bboxs:
            for bbox in bboxs:
                center = bbox["center"]
                x, y, w, h = bbox['bbox']
                pos_bx_x = x + w // 2
                pos_bx_y = y + h // 2
                score = int(bbox['score'][0] * 100)

                # Display the face's score and bounding box
                cvzone.putTextRect(frame, f'{score}%', (x, y - 10))
                cvzone.cornerRect(frame, (x, y, w, h))
                cv2.circle(frame, center=center, radius=4, color=(50, 255, 125), thickness=-1)

        # Check if we have valid positions for the face
        if pos_bx_x is not None and pos_bx_y is not None:
            # Set the polygon zone color based on the face's position
            if 200 < pos_bx_y < 280 and 280 < pos_bx_x < 360:
                sv_color = sv.Color.green()  # Face is inside the zone, turn the zone green
            else:
                sv_color = sv.Color.red()  # Face is outside the zone, keep the zone red

            # Define the polygon zone and annotate it
            zone = sv.PolygonZone(polygon=ZONE_POLYGON, frame_resolution_wh=[640, 480])
            zone_anno = sv.PolygonZoneAnnotator(zone=zone, color=sv_color, text_padding=0, text_scale=0)
            frame = zone_anno.annotate(scene=frame)

            # Annotate object detection boxes
            labels = [
                f"{model.model.names[class_id]} {confidence:0.2f}"
                for _, confidence, class_id, _ in detections]
            frame = box_an.annotate(scene=frame, detections=detections, labels=labels)

            # Draw 16x16 grid and highlight the cell containing the face
            for i in range(16):
                for j in range(16):
                    # Define the position of the grid cell
                    top_left = (j * cell_width, i * cell_height)
                    bottom_right = ((j + 1) * cell_width, (i + 1) * cell_height)
                    color = (0, 150, 250)  # Default grid cell color

                    # If the face is inside this grid cell, change the cell color to green
                    if top_left[0] <= pos_bx_x < bottom_right[0] and top_left[1] <= pos_bx_y < bottom_right[1]:
                        color = (0, 255, 0)  # Green color for the cell containing the face
                        green_cell_number = (15 - i) * 16 + j + 1  # Calculate the cell number

                    # Draw the grid cell and label it with its number
                    cv2.rectangle(frame, top_left, bottom_right, color, 1)
                    cell_number = (15 - i) * 16 + j + 1
                    text_position = (top_left[0] + 5, top_left[1] + 20)
                    cv2.putText(frame, f"{cell_number}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 155, 120), 1)

        # If the green cell was detected, send its number to the serial port
        if green_cell_number:
            send_position_to_serial(green_cell_number)

        # Show the frame with all annotations
        cv2.imshow("yolov8", frame)

        # Exit the loop if the ESC key is pressed
        if cv2.waitKey(30) == 27:
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()
    ser.close()  # Close the serial port

if __name__ == "__main__":
    main()
