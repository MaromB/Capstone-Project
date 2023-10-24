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

    def find_structure_shape(self):
        self.selected_image = self.images[10]
        if self.selected_image is not None:
            gray_image = cv2.cvtColor(self.selected_image, cv2.COLOR_BGR2GRAY)
            _, thresholded = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                canvas = np.zeros(self.selected_image.shape, dtype=np.uint8)
                cv2.drawContours(canvas, [largest_contour], -1, (0, 0, 255), 1)
                result = cv2.add(self.selected_image, canvas)
                cv2.imshow("Structure Shape", result)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

    def is_point_inside_polygon(point, polygon):
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            x_intersection = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= x_intersection:
                                inside = not inside
            p1x, p1y = p2x, p2y

        return inside

if __name__ == '__main__':
    image_manager = ImageManager()
    image_path = "your_image.jpg"  # Replace with the path to your image
    image_manager.load_images()
    image_manager.find_structure_shape()
