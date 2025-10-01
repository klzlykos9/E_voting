import face_recognition
import cv2
import imutils
import numpy as np
import pickle
import json
import sys
import os
import sqlite3
import csv

def printjson(type, message):
    print(json.dumps({type: message}))
    sys.stdout.flush()

def run_query(query, parameters=()):
    db_name = "students.db"
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        query_result = cursor.execute(query, parameters)
        conn.commit()
    return query_result

def viewing_all_records():
    all_records = []
    query = 'SELECT * FROM person'
    db_rows = run_query(query)
    for row in db_rows:
        all_records.append(row)
    return all_records

def generateCsv(fileName, names):
    header = ['Roll No.', 'Name', 'Gender', 'DOB', 'Mobile', 'Attendance']
    data = []
    all_records = viewing_all_records()

    for row in all_records:
        if row[1] in names:
            data.append([row[0], row[1], row[2], row[3], row[4], 'Present'])
        else:
            data.append([row[0], row[1], row[2], row[3], row[4], 'Absent'])

    with open(fileName, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


def load_model():
    encodings_path = "model/encodings.pickle"
    return pickle.loads(open(encodings_path, "rb").read())
    
def check(originalFrame, data):
    # Default configuration
    cascade_path = "haarcascade_frontalface_default.xml"
    encodings_path = "model/encodings.pickle"
    detection_method = "hog"
    face_method = "dnn"
    tolerance = 0.4

    # Load encodings
    printjson("status", "loading encodings...")
    
    # Load face detector
    detector = cv2.CascadeClassifier(cascade_path)

    # Prepare the frame
    frame = imutils.resize(originalFrame, width=500)

    # Face detection based on method
    if face_method == "dnn":
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model=detection_method)
    elif face_method == "haar":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, 
                                          minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # Compute facial encodings
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    # Recognize faces
    for encoding in encodings:
        distances = face_recognition.face_distance(data["encodings"], encoding)
        minDistance = min(distances) if len(distances) > 0 else 1.0

        if minDistance < tolerance:
            idx = np.where(distances == minDistance)[0][0]
            name = data["names"][idx]
        else:
            name = "unknown"
        names.append(name)

    # Draw rectangles and names
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 1)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    return frame, names