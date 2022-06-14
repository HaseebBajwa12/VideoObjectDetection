import gc
import glob
import logging
import os
import re

import torch
from . import Images_from_Video

from .celebrity_detection.celebrity_detection import CelebrityDetector


class DetectObject:
    """
    Detect Object in Images.
    """

    def __init__(self):
        self.__frames_time = {}
        self.__model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)
        self.response = {}
        """
                Create and configure logger
                """
        logging.basicConfig(filename="newfile.log",
                            format='%(asctime)s %(message)s',
                            filemode='w')
        """
        Creating an object
        """
        self.logger = logging.getLogger()
        """
        Setting the threshold of logger to DEBUG
        """
        self.logger.setLevel(logging.DEBUG)
        self.__result_list = []  # List of DataFrame

        self.__celeb_detector = CelebrityDetector()


    def dir_handling(self):
        """
        delete all images in these directories
        else create new directory
        """
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + "processed/"
        if os.path.isdir(path):
            for f in os.listdir(path):
                os.remove(os.path.join(path, f))
        else:
            os.makedirs(path)

        dir = os.path.dirname(os.path.abspath(__file__)) + '/' + "original_frames/"
        if os.path.isdir(dir):
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
        else:
            os.mkdir(dir)

    def video_to_images(self, f_name):
        self.dir_handling()
        """
        :param video filename:
        :return processed images:
        """
        img = Images_from_Video.ImagesFromVideo(self.logger,
                                                f_name)
        cam = img.readfile()
        self.__frames_time = img.get_frames_times(cam)

        if "Error Message" in self.__frames_time:
            return self.__frames_time
        img.processing(cam)
        img.detect_duplicate_images()
        images = glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/' +
                           "processed/*.jpg")
        return images

    def time_stamp_consistency(self, tm_obj) -> dict:
        """
        Consistent the timestamp of detected objects
        Parameters:

            tm_obj (dict): contains the list of all object and frames

        Returns:
            tm_obj (dict): Updated result dictionary with consistent timestamp
        """
        # Timestamp consistency
        for objs in tm_obj.keys():
            tm_obj[objs]['time'].sort()
            temp = tm_obj[objs]['time']

            time_stamp_loc = 1
            new_time_stamp = [temp[0]]
            new_time_loc = 0
            while time_stamp_loc < len(temp):
                if (int(new_time_stamp[new_time_loc][1]) - int(temp[time_stamp_loc][0])) == -1 or (
                        int(new_time_stamp[new_time_loc][1]) - int(temp[time_stamp_loc][0]) == 0):
                    new_time_stamp[new_time_loc] = [new_time_stamp[new_time_loc][0], temp[time_stamp_loc][1]]

                else:
                    new_time_stamp.append([temp[time_stamp_loc][0], temp[time_stamp_loc][1]])
                    new_time_loc += 1
                time_stamp_loc += 1
            tm_obj[objs]['time'] = new_time_stamp
        return tm_obj

    def get_Processed_frames_name(self):
        try:
            path = os.path.dirname(os.path.abspath(__file__)) + '/' + "processed/"
            images = glob.glob(path + "*.jpg")
            return images
        except Exception as e:
            self.logger.error(e)

    def detect_objects(self, image):
        """
        Take Image and return detected objects information.
        Parameters:
            image:
        Returns:
        """

        print(f'processing {len(image)}')
        total = 0
        classes_count = {'celebrity': 0}
        detected_celeb = {}
        for slice in range(0, len(image), 100):

            if slice + 100 < len(image):
                result = self.__model(image[slice:slice + 100])
                self.__result_list.extend(result.pandas().xyxy)
            else:
                result = self.__model(image[slice:])
                self.__result_list.extend(result.pandas().xyxy)

        for frame_id, frame in enumerate(self.__result_list):
            detected_classes = set(frame['name'])
            list_objects = list(frame['name'])
            for obj in detected_classes:
                time = []
                frames_name = []
                regex = re.compile(r'(\d+|\s+)')
                name = int(regex.split(image[frame_id])[-2])
                initial_time = round(name / self.__frames_time["frames_per_second"], 2)
                end_time = round((name + 1) / self.__frames_time["frames_per_second"], 2)
                if obj in classes_count:
                    classes_count[obj] += list_objects.count(obj)
                    time = self.response[obj]["time"]
                    frames_name = self.response[obj]["frames"]
                else:
                    self.response[obj] = {}
                    classes_count[obj] = list_objects.count(obj)

                if obj == 'person':
                    celeb = self.__celeb_detector.get_celeb(image[frame_id])
                    classes_count['celebrity'] += len(celeb.keys())
                    for celeb_name, celeb_img in celeb.items():
                        if celeb_name not in detected_celeb:
                            classes_count['celebrity'] += len(celeb.keys())

                            detected_celeb[celeb_name] = {
                                'time': [[initial_time, end_time]],
                                'frames': [celeb_img]
                            }
                        else:

                            detected_celeb[celeb_name]['time'].append([initial_time, end_time]),
                            detected_celeb[celeb_name]['frames'].append(celeb_img)

                time.append([initial_time, end_time])
                frames_name.append(image[frame_id])
                self.response[obj]["time"] = time
                self.response[obj]["frames"] = frames_name
                total += list_objects.count(obj)

        classes_count['All'] = total

        # Timestamp consistency
        for objs in self.response.keys():
            self.response[objs]['time'].sort()
            temp = self.response[objs]['time']

            time_stamp_loc = 1
            new_time_stamp = [temp[0]]
            new_time_loc = 0
            while time_stamp_loc < len(temp):
                if (int(new_time_stamp[new_time_loc][1]) - int(temp[time_stamp_loc][0])) == -1 or (
                        int(new_time_stamp[new_time_loc][1]) - int(temp[time_stamp_loc][0]) == 0):
                    new_time_stamp[new_time_loc] = [new_time_stamp[new_time_loc][0], temp[time_stamp_loc][1]]

                else:
                    new_time_stamp.append([temp[time_stamp_loc][0], temp[time_stamp_loc][1]])
                    new_time_loc += 1
                time_stamp_loc += 1
            self.response[objs]['time'] = new_time_stamp

        detected_celeb = self.time_stamp_consistency(detected_celeb)

        return {
            'video_duration': self.__frames_time["video_time"],
            'objects_count': classes_count,
            'objects_loc': self.response,
            'celebrity': detected_celeb
        }
