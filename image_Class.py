import math
import cv2
import os
import numpy as np
from PIL import Image, ImageTk


def simplify_points(point_list, distance_threshold):
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


def cv_image_to_photoimage(cv_image):
    # Convert the color from BGR to RGB
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    # Convert to an ImageTk.PhotoImage object
    pil_image = Image.fromarray(cv_image)
    photo_image = ImageTk.PhotoImage(image=pil_image)
    return photo_image


class ImageManager:
    def __init__(self):
        self.shape_boundary = None
        self.shape_polygon = None
        self.frame_image = None
        self.original_image = None
        self.contours = []
        self.preloaded_images = {}

    def load_image(self, num_of_image):
        # Marom - C:/Users/Administrator/Downloads/Capstone-Project/project photos/
        folder_path1 = "C:/Users/Administrator/Downloads/Capstone-Project/project photos/"
        image_filename1 = num_of_image + ".jpg"
        image_path1 = os.path.join(folder_path1, image_filename1)
        self.frame_image = cv2.imread(image_path1)
        folder_path2 = "C:/Users/Administrator/Downloads/Capstone-Project/project photos/before"
        image_filename2 = num_of_image + ".jpg"
        image_path2 = os.path.join(folder_path2, image_filename2)
        # self.original_image = self.frame_image
        self.original_image = cv2.imread(image_path2)

    def preload_images(self, start_num, end_num):
        for i in range(start_num, end_num + 1):
            frame_path = os.path.join("C:/Users/Administrator/Downloads/Capstone-Project/project photos/", f"{i}.jpg")
            original_path = os.path.join("C:/Users/Administrator/Downloads/Capstone-Project/project photos/before/",
                                         f"{i}.jpg")

            # Load and resize the frame image
            frame_image = cv2.imread(frame_path)
            resized_frame_image = cv2.resize(frame_image, (150, 150))
            # Convert to PhotoImage
            frame_photo_image = cv_image_to_photoimage(resized_frame_image)

            # Load and resize the original image
            original_image = cv2.imread(original_path)
            resized_original_image = cv2.resize(original_image, (250, 250))
            # Convert to PhotoImage
            original_photo_image = cv_image_to_photoimage(resized_original_image)

            # Store in the dictionary
            self.preloaded_images[i] = (frame_photo_image, original_photo_image)

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
        simplified_shape_boundary = simplify_points(self.shape_boundary, distance_threshold)

        self.shape_polygon = cv2.approxPolyDP(np.array(simplified_shape_boundary), epsilon=3, closed=True)
        return self.shape_polygon
