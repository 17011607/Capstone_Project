from sklearn.metrics.pairwise import pairwise_distances
from tensorflow.python.platform import gfile
import tensorflow.compat.v1 as tf
import numpy as np
import detect_and_align
import argparse
import easygui
import socket
import time
import cv2
import os
import datetime
import threading
import json

from gestures.tello_gesture_controller import TelloGestureController
from utils import CvFpsCalc
from drone_manager import DroneManager
from gestures import *

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

class IdData:
    """Keeps track of known identities and calculates id matches"""

    def __init__(
        self, id_folder, mtcnn, sess, embeddings, images_placeholder, phase_train_placeholder, distance_treshold
    ):
        print("Loading known identities: ", end="")
        self.distance_treshold = distance_treshold
        self.id_folder = id_folder
        self.mtcnn = mtcnn
        self.id_names = []
        self.embeddings = None

        image_paths = []
        os.makedirs(id_folder, exist_ok=True)
        ids = os.listdir(os.path.expanduser(id_folder))
        if not ids:
            return

        for id_name in ids:
            id_dir = os.path.join(id_folder, id_name)
            print(f"id_dir {id_dir} / id_name {id_name}")
            image_paths = image_paths + [os.path.join(id_dir, img) for img in os.listdir(id_dir)]

        print("Found %d images in id folder" % len(image_paths))
        aligned_images, id_image_paths = self.detect_id_faces(image_paths)
        feed_dict = {images_placeholder: aligned_images, phase_train_placeholder: False}
        self.embeddings = sess.run(embeddings, feed_dict=feed_dict)

        if len(id_image_paths) < 5:
            self.print_distance_table(id_image_paths)

    def add_id(self, embedding, new_id, face_patch):
        if self.embeddings is None:
            self.embeddings = np.atleast_2d(embedding)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])
        self.id_names.append(new_id)
        id_folder = os.path.join(self.id_folder, new_id)
        os.makedirs(id_folder, exist_ok=True)
        filenames = [s.split(".")[0] for s in os.listdir(id_folder)]
        numbered_filenames = [int(f) for f in filenames if f.isdigit()]
        img_number = max(numbered_filenames) + 1 if numbered_filenames else 0
        cv2.imwrite(os.path.join(id_folder, f"{img_number}.jpg"), face_patch)

    def detect_id_faces(self, image_paths):
        aligned_images = []
        id_image_paths = []
        for image_path in image_paths:
            image = cv2.imread(os.path.expanduser(image_path), cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_patches, _, _ = detect_and_align.detect_faces(image, self.mtcnn)
            if len(face_patches) > 1:
                print(
                    "Warning: Found multiple faces in id image: %s" % image_path
                    + "\nMake sure to only have one face in the id images. "
                    + "If that's the case then it's a false positive detection and"
                    + " you can solve it by increasing the thresolds of the cascade network"
                )
            aligned_images = aligned_images + face_patches
            id_image_paths += [image_path] * len(face_patches)
            path = os.path.dirname(image_path)
            self.id_names += [os.path.basename(path)] * len(face_patches)

        return np.stack(aligned_images), id_image_paths

    def print_distance_table(self, id_image_paths):
        """Prints distances between id embeddings"""
        distance_matrix = pairwise_distances(self.embeddings, self.embeddings)
        image_names = [path.split("/")[-1] for path in id_image_paths]
        print("Distance matrix:\n{:20}".format(""), end="")
        [print("{:20}".format(name), end="") for name in image_names]
        for path, distance_row in zip(image_names, distance_matrix):
            print("\n{:20}".format(path), end="")
            for distance in distance_row:
                print("{:20}".format("%0.3f" % distance), end="")
        print()

    def find_matching_ids(self, embs):
        if self.id_names:
            matching_ids = []
            matching_distances = []
            distance_matrix = pairwise_distances(embs, self.embeddings)
            for distance_row in distance_matrix:
                min_index = np.argmin(distance_row)
                if distance_row[min_index] < self.distance_treshold:
                    matching_ids.append(self.id_names[min_index])
                    matching_distances.append(distance_row[min_index])
                else:
                    matching_ids.append(None)
                    matching_distances.append(None)
        else:
            matching_ids = [None] * len(embs)
            matching_distances = [np.inf] * len(embs)
        return matching_ids, matching_distances

def load_model(model):
    model_exp = os.path.expanduser(model)
    if os.path.isfile(model_exp):
        print("Loading model filename: %s" % model_exp)
        with gfile.GFile(model_exp, "rb") as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name="")
    else:
        raise ValueError("Specify model file, not directory!")



def main(space, name):
    global gesture_buffer
    global gesture_id
    global temp_x
    global temp_y
    global x_deviation
    global y_deviation 
    temp_x = 217 # +- 5
    temp_y = 253 # +- 5
    x_deviation = 10
    y_deviation = 10
    t_x = 0
    t_y = 0
    t_z = 0
    t_degree = 0
    in_flight = False
    timer = 0
    gesture = [0 for i in range(7)]
    drone_ip='192.168.10.1'
    drone_port = 8889
    drone_address=(drone_ip,drone_port)
    command_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    
    with open("gesture.json","r") as f:
        data = json.load(f)
        for i in range(7):
            gesture[i] = data[str(i)]

    
    

    def adjust_tello_position(offset_x, offset_y, offset_z, length_x, length_y):
        global temp_x
        global temp_y
        drone_x, drone_y, drone_z, degree = 0, 0, 0, 0
        print(f"offset_x : {offset_x}, offset_y : {offset_y}, offset_z : {offset_z}, length_x : {length_x}, length_y : {length_y}, temp_x : {temp_x}, temp_y : {temp_y}")
        if temp_y - y_deviation*3 <= length_y <= temp_y + y_deviation*3 and not(temp_x - x_deviation <= length_x <= temp_x + x_deviation):
            print("CW!")
            if offset_x < -30:
                degree = -10
            elif offset_x > 30 :
                degree = 10

        if offset_x < -30:
            print("left")
            drone_x = -10
        if offset_x > 30:
            print("right")
            drone_x = 10

        if offset_y < -15:
            print("down")
            drone_y = -10
        if offset_y > 15:
            print("up")
            drone_y = 10

        if offset_z > 0.30:
            print("back")
            drone_z = -10
        if offset_z < 0.02:
            print("forward")
            drone_z = 10
        if t_x != drone_x and t_y != drone_y and t_z != drone_z and t_degree != degree:
            command_socket.sendto(f"rc {drone_x} {drone_z} {drone_y} {degree}".encode('utf-8'), drone_address)
            t_x = drone_x
            t_y = drone_y
            t_z = drone_z
            t_degree = degree
                
    def snapshot(frame):
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        p = os.path.sep.join(("./", filename))

        cv2.imwrite(p, frame)
        print("[INFO] saved {}".format(filename))
        
    def set_length(length_x, length_y):
        global temp_x
        global temp_y
        print("Set_length")
        temp_x = length_x
        temp_y = length_y

    def gesture_action(label,frame):
        if label == "0":
            command_socket.sendto(f"rc 0 0 0 0".encode('utf-8'), drone_address)
        elif label == "1":
            command_socket.sendto(f'land'.encode('utf-8'), drone_address)
        elif label == "2":
            threading.Timer(timer, snapshot,args=(frame,)).start() # time snapshot
        elif label == "3":
            command_socket.sendto(f"left 20".encode('utf-8'), drone_address)
        elif label == "4":
            command_socket.sendto(f"right 20".encode('utf-8'), drone_address)
        elif label == "5":
            command_socket.sendto(f"up 20".encode('utf-8'), drone_address)
        elif label == "6":
            command_socket.sendto(f"down 20".encode('utf-8'), drone_address)

    gesture_controller = TelloGestureController()

    gesture_detector = GestureRecognition('store_true', 0.7,0.5)
    gesture_buffer = GestureBuffer(buffer_len=5)
        
    cv_fps_calc = CvFpsCalc(buffer_len=10)
        
    mode = 0
    number = -1
    cnt = 0
    
    distance_treshold = 0.95
    with tf.Graph().as_default():
        with tf.Session() as sess:
            # Setup models
            mtcnn = detect_and_align.create_mtcnn(sess, None)

            load_model('./data/20180402-114759.pb')
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

            # Load anchor IDs
            id_data = IdData(
                space, mtcnn, sess, embeddings, images_placeholder, phase_train_placeholder, distance_treshold)
                
            cap = cv2.VideoCapture('udp://@0.0.0.0:5000',cv2.CAP_FFMPEG)
                
            if not cap.isOpened():
                cap.open('udp://@0.0.0.0:5000')

            frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

            center_x = int(frame_width/2) * 0.75
            center_y = int(frame_height/2) * 0.75

            show_data = False
            frame_detections = None
            cnt = 0
            number = -1
            

            while True:
                chk = 0
                ret, frame = cap.read()
                
                # Locate faces and landmarks in frame
                if ret:
                    time.sleep(0.01)
                    frame = cv2.resize(frame, (0,0), fx=0.75, fy=0.75)
                    if cnt % 20 < 1 :
                        face_patches, padded_bounding_boxes, landmarks = detect_and_align.detect_faces(frame, mtcnn)

                        if len(face_patches) > 0:
                            face_patches = np.stack(face_patches)
                            feed_dict = {images_placeholder: face_patches, phase_train_placeholder: False}
                            embs = sess.run(embeddings, feed_dict=feed_dict)

                            matching_ids, matching_distances = id_data.find_matching_ids(embs)
                            frame_detections = {"embs": embs, "bbs": padded_bounding_boxes, "frame": frame.copy()}

                            print("Matches in frame:")
                            for bb, landmark, matching_id, dist in zip(
                                padded_bounding_boxes, landmarks, matching_ids, matching_distances):
                                chk = 0
                                if matching_id is None:
                                    matching_id = "Unknown"
                                    print("Unknown! Couldn't fint match.")
                                else:
                                    if matching_id == name:
                                        chk = 1
                                    print("Hi %s! Distance: %1.4f" % (matching_id, dist))

                                            
                                if chk == 1 :
                                    framebak = frame.copy()
                                    
                                    if show_data:
                                        cv2.putText(frame, matching_id, (bb[0], bb[3]), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
                                        cv2.rectangle(frame, (bb[0], bb[1]), (bb[2], bb[3]), (255, 0, 0), 2)
                                        cv2.rectangle(frame, (bb[2], bb[1]), (2*bb[2] - bb[0], bb[3]), (255, 0, 0), 2)
                                        
                                    fps = cv_fps_calc.get()

                                    cv2.rectangle(frame, (bb[2], bb[1]), (2*bb[2] - bb[0], bb[3]), (255, 0, 0), 2)
                                                        
                                    image = frame[bb[1]:bb[3], bb[2]:2*bb[2] - bb[0]].copy()
                                    debug_image, gesture_id = gesture_detector.recognize(image, number, mode)
                                    gesture_buffer.add_gesture(gesture_id)
                                    gesture_controller.gesture_control(gesture_buffer)
                                    debug_image = gesture_detector.draw_info(debug_image, fps, mode, number)
                                    #cv2.imshow('Gesture Recognition', debug_image)
                                    
                                    face_center_x = bb[0] + int((bb[2]-bb[0])/2)
                                    face_center_y = bb[1] + int((bb[3]-bb[1])/2)
                                    z_area = (bb[2]-bb[0]) * (bb[3]-bb[1])
                                    length_x = bb[2] - bb[0]
                                    length_y = bb[3] - bb[1]

                                    offset_x = face_center_x - center_x
                                    offset_y = face_center_y - center_y - 30
                                    
                                    if gesture_id == 0:
                                        gesture_action(gesture[0],framebak)
                                    elif gesture_id == 1:
                                        gesture_action(gesture[1],framebak)
                                    elif gesture_id == 2:
                                        gesture_action(gesture[2],framebak)
                                    elif gesture_id == 3:
                                        gesture_action(gesture[3],framebak)
                                    elif gesture_id == 4:
                                        gesture_action(gesture[4],framebak)
                                    elif gesture_id == 5:
                                        gesture_action(gesture[5],framebak)
                                    elif gesture_id == 6:
                                        gesture_action(gesture[6],framebak)
                                        
                                    print(f"bb[0] : {bb[0]}, bb[1] : {bb[1]}, bb[2] : {bb[2]}, bb[3] : {bb[3]}, face_center_x : {face_center_x}, face_center_y : {face_center_y}")
                                    adjust_tello_position(offset_x, offset_y, z_area, length_x, length_y)
                        else:
                            print("Couldn't find a face")

                    #cv2.imshow("Face Recognition", frame)
                    cnt+=1
                    key = cv2.waitKey(1) & 0xff
                    if key == 27:  # ESC
                        break
                                
                else:  
                    print("ret : false") 
                    cap.release()
                    cap = cv2.VideoCapture('udp://@0.0.0.0:5000')       

            cap.release()
            cv2.destroyAllWindows()

            

if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("id_folder", type=str, nargs="+", help="Folder containing ID folders")
    parser.add_argument("user", type=str, help="Select User")
    parser.add_argument("-t", "--threshold", type=float, help="Distance threshold defining an id match", default=0.95)
    print(type(parser.parse_args()))
    main(parser.parse_args())
