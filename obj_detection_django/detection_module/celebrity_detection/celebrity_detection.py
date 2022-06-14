import os
import random

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model


class CelebrityDetector:
    def __init__(self):
        """
        Setting model weights and celeb names index file.
        """
        self.handle_extracted_faces()
        names_file = os.path.dirname(os.path.abspath(__file__)) + '/' + 'celeb_name.csv'
        model_file = os.path.dirname(os.path.abspath(__file__)) + '/' + 'model weights/Weights Face Recognitions.h5'
        face_cascade = os.path.dirname(os.path.abspath(__file__)) + '/' + 'cascade/haarcascade_frontalface_default.xml'
        self.detected_faces = os.path.dirname(os.path.abspath(__file__)) + '/' + 'detected celebrity'
        if not os.path.exists(self.detected_faces):
            os.mkdir(self.detected_faces)
        else:
            files = os.listdir(self.detected_faces)
            for file in files:
                os.remove(self.detected_faces + '/' + file.strip())

        if not os.path.isfile(model_file):
            raise FileNotFoundError('Model Weights not Found.')

        if not os.path.isfile(names_file):
            raise FileNotFoundError('Celebrity index file not Found.')

        if not os.path.isfile(face_cascade):
            raise FileNotFoundError('haarcascade file not Found.')

        self.model = load_model(model_file)
        self.face_cascade = cv2.CascadeClassifier(face_cascade)

        self.__classes = open(names_file, 'r')

        self.__classes = [name.strip() for name in self.__classes.readlines()]
        self.__classes.sort()

        self.rows = 160
        self.cols = 160

    def __faces_from_image(self, image_path) -> None:
        """
        Message:
            Take Image_path and extract all faces exist in it.
        Parameters:
            image_path (str): Path of Image
        Returns:
            None
        """
        # Cleaning folder to make place for new faces.
        self.handle_extracted_faces()

        # Reading Image for processing
        img = cv2.imread(image_path)

        # Convert into grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        # faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.4,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Draw rectangle around the faces and crop the faces
        for (x, y, w, h) in faces:

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            face = img[y:y + h, x:x + w]

            cv2.imwrite(os.path.dirname(os.path.abspath(__file__)) + '/' + f'extracted faces/face{x+y}.jpg', face)

    def get_celeb(self, image_path) -> dict:
        """
        Message:
            Take image and detect celebrity in it.
        Parameters:
            image_path (str): Path of Image to identify
        Returns:
            result (dict):
                key: celebrity_name (str): Name of celebrity in Image.
                value: celebrity_Image (np.array): Detected image of celebrity.
        """
        if not os.path.isfile(image_path):
            raise FileNotFoundError('Image File Not Found at given path.')

        result = {}
        self.__faces_from_image(image_path)
        files = os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/' + 'extracted faces')
        for file in files:
            full_image_path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'extracted faces/' + file.strip()
            temp_image = cv2.imread(full_image_path)

            img = tf.keras.preprocessing.image.load_img(
                full_image_path, target_size=(self.rows, self.cols)
            )

            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)  # Create a batch
            img_array = img_array / 255.

            score = self.model.predict(img_array)
            detected_celeb = self.__classes[np.argmax(score)]

            if detected_celeb:
                result[detected_celeb] = temp_image
                celeb_path = self.detected_faces + '/' + f'{detected_celeb}.jpg'
                cv2.imwrite(celeb_path, temp_image)
                result[detected_celeb] = celeb_path

        return result

    def detect_celeb_in_image(self, image_path):
        """
        Message:
            Take Image path and draw mark celebrity in it.
        Parameters:
            image_path (str): Path of Image
        Returns:
            Image (np.array): Image with marked celebrity in the
                              form of numpy array.
        """

        if not os.path.isfile(image_path):
            raise FileNotFoundError('Image File Not Found at given path.')

        real_image = cv2.imread(image_path)

        # Convert into grayscale
        gray = cv2.cvtColor(real_image, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            rand_color = (random.randint(100, 200), random.randint(150, 255), random.randint(0, 255))
            cv2.rectangle(real_image, (x, y), (x + w, y + h), rand_color, 2)
            faces = real_image[y:y + h, x:x + w]
            cv2.imwrite(os.path.dirname(os.path.abspath(__file__)) + '/' + f'temp files/face{x+y}.jpg', faces)

            full_image_path = os.path.dirname(os.path.abspath(__file__)) + '/' + f'temp files/face{x+y}.jpg'

            img = tf.keras.preprocessing.image.load_img(
                full_image_path, target_size=(self.rows, self.cols)
            )

            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)  # Create a batch
            img_array = img_array / 255.

            score = self.model.predict(img_array)
            detected_celeb = self.__classes[np.argmax(score)]
            cv2.putText(real_image, detected_celeb, (x, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, rand_color, 1)
        cv2.imwrite(os.path.dirname(os.path.abspath(__file__)) + '/' + f'result/result.jpg', real_image)
        return real_image

    @staticmethod
    def handle_extracted_faces():
        """
        Message:
            Delete previous faces from folder to save
            new faces.
            Parameters:
            Returns:
                None
        """
        if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/' + 'extracted faces'):
            files = os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/' + 'extracted faces')
            for file in files:
                os.remove(os.path.dirname(os.path.abspath(__file__)) + '/' + 'extracted faces/' + file.strip())
        else:
            os.mkdir(os.path.dirname(os.path.abspath(__file__)) + '/' + 'extracted faces')

        if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/' + 'temp files'):
            files = os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/' + 'temp files')
            for file in files:
                os.remove(os.path.dirname(os.path.abspath(__file__)) + '/' + 'temp files/' + file.strip())
        else:
            os.mkdir(os.path.dirname(os.path.abspath(__file__)) + '/' + 'temp files')
