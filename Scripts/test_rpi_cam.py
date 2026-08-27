import cv2

cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)

print("Camera opened:", cap.isOpened())

if not cap.isOpened():
    print("Failed to open camera")
    exit()

ret, frame = cap.read()

print("Frame captured:", ret)

if ret:
    print("Frame shape:", frame.shape)
    cv2.imwrite("camera_test.jpg", frame)

cap.release()
