import time

import numpy as np
from cv2 import dnn, rectangle, putText, FONT_HERSHEY_SIMPLEX


class ObjectDetector:
    def __init__(self, w, h):
        self.boxes = []
        self.confidences = []
        self.class_ids = []
        self.outputs = []
        self.boundingBoxes = []

        self.image = None
        self.drawn_image = None

        self.w = w
        self.h = h

        self.propagationTime = 0
        self.extractionTime = 0
        self.drawingTime = 0

        print('Loading YOLOv3 net')
        self.net = dnn.readNetFromDarknet('data/yolov3.cfg', 'data/yolov3.weights')
        self.net.setPreferableBackend(dnn.DNN_BACKEND_OPENCV)

        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i - 1] for i in self.net.getUnconnectedOutLayers()]

        print('Reading class names')
        self.classes = open('coco.names').read().strip().split('\n')

        print('Generating colors')
        self.colors = np.random.randint(0, 255, size=(len(self.classes), 3), dtype='uint8')

    def detect(self, image):
        self.image = image

        blob = dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)

        tf0 = time.time()
        self.outputs = self.net.forward(self.ln)
        tf = time.time()

        self.boxes, self.confidences, self.class_ids = self.extract_results()
        te = time.time()

        self.drawn_image = self.draw_boxes()
        td = time.time()

        self.propagationTime = tf - tf0
        self.extractionTime = te - tf
        self.drawingTime = td - te

    def extract_results(self):
        boxes = []
        confidences = []
        class_ids = []

        for output in self.outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5:
                    box = detection[:4] * np.array([self.w, self.h, self.w, self.h])
                    (centerX, centerY, wBox, hBox) = box.astype("int")

                    x_box = centerX - wBox // 2
                    y_box = centerY - hBox // 2

                    box = (x_box, y_box, int(wBox), int(hBox))
                    boxes.append(box)
                    confidences.append(confidence)
                    class_ids.append(class_id)

        return boxes, confidences, class_ids

    def draw_boxes(self):
        indices = dnn.NMSBoxes(self.boxes, self.confidences, 0.5, 0.4)

        if len(indices) > 0:
            self.boundingBoxes = []

            for i in indices.flatten():
                class_id = self.class_ids[i]
                color = [int(c) for c in self.colors[class_id]]

                (xBox, yBox, wBox, hBox) = self.boxes[i]

                rectangle(self.image, (xBox, yBox), (xBox + wBox, yBox + hBox), color, 2)

                label = f'{self.classes[class_id]} (confidence {self.confidences[i]:.4f})'
                putText(self.image, label, (xBox, yBox - 5), FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                self.boundingBoxes.append(((xBox, yBox), (wBox, hBox), self.classes[class_id], self.confidences[i]))

        return self.image
