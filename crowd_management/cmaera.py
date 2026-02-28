from ultralytics import YOLO
import cv2
import requests

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(https://10.141.231.107:8080/)

if not cap.isOpened():
    print("Camera not working")
    exit()

THRESHOLD = 5 

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.4)

    person_count = 0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if model.names[cls] == "person":
                person_count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

  
    status = "LOW"
    color = (0, 255, 0)
    if person_count > THRESHOLD:
        status = "HIGH - ALERT!"
        color = (0, 0, 255)

    cv2.putText(frame, f"Persons: {person_count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"Status: {status}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # API Reporting
    try:
        requests.post("http://localhost:5000/camera-update", 
                      json={"person_count": person_count}, 
                      timeout=1)
    except Exception as e:
        print(f"Server sync failed: {e}")


    cv2.imshow("Crowd Detection - Laptop Camera", frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
