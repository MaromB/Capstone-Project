import math
import cv2
import os
import numpy as np


class ImageManager:
    def __init__(self):
        self.shape_coordinates = None
        self.hierarchy = None
        self.images = []
        self.selected_image = None
        self.contours = []
        self.shape_coordinates = []

    def load_images(self):
        folder_path = "C:/Users/Administrator/Downloads/Capstone-Project/project photos"
        image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

        for image_file in image_files:
            images_path = os.path.join(folder_path, image_file)
            image = cv2.imread(images_path)
            self.images.append(image)

    def find_structure_shape(self, num_of_photo):
        self.selected_image = self.images[num_of_photo]
        shape_boundary = []

        if self.selected_image is not None:
            gray_image = cv2.cvtColor(self.selected_image, cv2.COLOR_BGR2GRAY)
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
                    shape_boundary.append((x, y))
                distance_threshold = 5

        simplified_shape_boundary = self.simplify_points(shape_boundary, distance_threshold)

        shape_polygon = cv2.approxPolyDP(np.array(simplified_shape_boundary), epsilon=3, closed=True)
        #point_to_check = (100, 803)
        #is_inside = cv2.pointPolygonTest(shape_polygon, point_to_check, measureDist=False)

        return shape_polygon


    def simplify_points(self, point_list, distance_threshold):
        simplified_list = []
        if len(point_list) > 0:
            simplified_list.append(point_list[0])  # Always keep the first point
        for i in range(1, len(point_list)):
            x1, y1 = point_list[i]
            x2, y2 = simplified_list[-1]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if distance >= distance_threshold:
                simplified_list.append((x1, y1))
        return simplified_list


if __name__ == '__main__':
    image_manager = ImageManager()
    image_manager.load_images()
    image_manager.find_structure_shape(1)
