import math
import cv2
import os
import numpy as np


class ImageManager:
    def __init__(self):
        self.shape_boundary = None
        self.shape_polygon = None
        self.frame_image = None
        self.original_image = None
        self.contours = []

    def load_image(self, num_of_image):
        folder_path1 = "C:/Users/Administrator/Downloads/Capstone-Project/project photos"
        image_filename1 = num_of_image + ".jpg"
        image_path1 = os.path.join(folder_path1, image_filename1)
        self.frame_image = cv2.imread(image_path1)

        folder_path2 = "C:/Users/Administrator/Downloads/Capstone-Project/project photos/before"
        image_filename2 = num_of_image + ".jpg"
        image_path2 = os.path.join(folder_path2, image_filename2)
        self.original_image = cv2.imread(image_path2)

    def find_structure_shape(self):
        self.shape_boundary = []
        if self.frame_image is not None:
            gray_image = cv2.cvtColor(self.frame_image, cv2.COLOR_BGR2GRAY)
            _, thresholded = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Find the largest contour
                largest_contour = max(contours, key=cv2.contourArea)

                # Convert largest_contour to a NumPy array
                largest_contour = np.array(largest_contour)

                # Extract the coordinates of the largest contour
                for point in largest_contour:
                    x, y = point[0]
                    self.shape_boundary.append((x, y))
                distance_threshold = 5

        simplified_shape_boundary = self.simplify_points(self.shape_boundary, distance_threshold)

        #simplified_shape_boundary *= 1.5
        self.shape_polygon = cv2.approxPolyDP(np.array(simplified_shape_boundary), epsilon=3, closed=True)
        return self.shape_polygon


    def simplify_points(self, point_list, distance_threshold):
        simplified_list = []
        if len(point_list) > 0:
            simplified_list.append(point_list[0])
        for i in range(1, len(point_list)):
            x1, y1 = point_list[i]
            x2, y2 = simplified_list[-1]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if distance >= distance_threshold:
                simplified_list.append((x1, y1))
        return simplified_list
