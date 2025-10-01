import cv2
import numpy as np
from video_capture import VideoCapture
import imutils
import constants
import voterface_recognition

def check_is_voter_valid(email):
    email = str(email).lstrip().rstrip()
    video_capture = VideoCapture(0)
    detected_student = {}

    
    counter = constants.face_checker_count

    while counter != 0:        
        frame = video_capture.read()
        out_frame = None

        try:
            out_frame, names = voterface_recognition.check(frame, voterface_recognition.load_model())
            for key in names:
                if detected_student.get(key) is not None:
                    detected_student[key] += 1
                else:
                    detected_student[key] = 1

            counter -= 1

        except Exception as e:
            print(e)
            out_frame = frame

        out_frame = imutils.resize(out_frame, width=1000, height=700)

        # Display the resulting image
        cv2.imshow('Marking attendance', out_frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(constants.frame_delay) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
 
    print('Detected voters:', detected_student)
    print("email",email)
    print(detected_student.get(email))
    # Check if the email is in detected_student and its count is greater than 13
    if detected_student.get(email, 0) > constants.min_count:
        return True
    return False


