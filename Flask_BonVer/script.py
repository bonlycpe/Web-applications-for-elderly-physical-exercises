import cv2
import pandas as pd
import numpy as np
import mediapipe as mp
import pickle

def camera_processing():

    # load model
    model = pickle.load(open(r"model/course_test/handup_model.pkl", 'rb'))

    # Grabbing the Holistic Model from Mediapipe and
    mp_holistic = mp.solutions.holistic

    # Initializing the Model
    holistic_model = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Initializing the drawing utils for drawing the facial landmarks on image
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        rat, frame = cap.read()

        # resizing the frame for better view
        frame = cv2.resize(frame, (640,480))
    
        # Converting the from BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image.flags.writeable = False

        # pass by reference.
        results = holistic_model.process(image)

        image.flags.writeable = True
    
        # Converting back the RGB image to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        mp_drawing.draw_landmarks(
            image, 
            results.pose_landmarks, 
            mp_holistic.POSE_CONNECTIONS,   
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )

        try:
            pose = results.pose_landmarks.landmark
            pose_row = list(np.array([[landmark.x,landmark.y,landmark.z,landmark.visibility] for landmark in pose]).flatten())

            # Make Detections
            X = pd.DataFrame([pose_row])
            predict_class = model.predict(X)[0]
            predict_prob = model.predict_proba(X)[0]

            coords = tuple(np.multiply(
            np.array(
                (results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].x, 
                results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].y))
            , [640,480]).astype(int))
                
            cv2.rectangle(image, 
                        (coords[0], coords[1]+5), 
                        (coords[0]+len(predict_class)*20, coords[1]-30), 
                        (245, 117, 16), -1)
            cv2.putText(image, predict_class, coords, 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        except:
            cv2.putText(image, str('Error')
                        , (210,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        frame = cv2.imencode('.jpeg', image)[1].tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')