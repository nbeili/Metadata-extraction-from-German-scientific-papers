from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

import re

import fitz

import base64

from io import BytesIO

import json

from itertools import groupby
import math
from collections import Counter

import numpy as np

class MetadataError(Exception):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors
        
class RectangleError(Exception):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class Paper:
    
    def __init__(self, filename, metadata_dict):
        self.filename = filename
        self.image = self.to_image()
        self.metadata = metadata_dict
        self.rectangles = {}
        self.annotations = []
        
    def __str__(self):
        return f"{self.filename}"
    
    def to_image(self,):
        img = convert_from_path(self.filename)[0]
        return img
    
    def resize_image(self, width=569, height=794):
        self.image = self.image.resize((width, height))
        
    
    def save_image(self,output_path=""):
        reg = re.compile("[^/]+$")
        img_name = re.search(reg, self.filename)[0][:-4] + ".jpeg"
        if len(output_path) != 0 and output_path[-1] != "/":
            output_path += "/"
        self.image.save(output_path + img_name)
        
    def get_metadata_items(self, metadata_df):
        reg = re.compile("[^/]+$")
        instance = re.search(reg, self.filename)[0][:-4] + ".docx"
        
        current = metadata_df[metadata_df["filenames"] == instance]
        for key in self.metadata.keys():
            self.metadata[key] += str(list(current[key])[0])
        
    def bbox_from_text(self):
        # get the first page
        doc = fitz.open(self.filename)
        page = doc[0]
        
        if list(self.metadata.values())[0] == "":
            raise MetadataError("No metadata values specified. Run method get_metadata_items(metadata_df) before callsing this method.", "")
        i = 0
        for key, val in self.metadata.items():
            self.rectangles[key] = page.searchFor(val, hit_max=1000)
            # handle hyphenated words
            if len(self.rectangles[key]) == 0:
                text = self.metadata[key].split("-")
                for part in text:
                    results = page.searchFor(part, hit_max=1000)
                    self.rectangles[key] += results
            # if more than one Rect was found, combine them
            if len(self.rectangles[key]) > 1:
                foundRectList = [tuple(rect) for rect in self.rectangles[key]]
    
                #find min x, min y, max x, max y
                min_x = foundRectList[0][0]
                min_y = foundRectList[0][1]
                max_x = foundRectList[0][2]
                max_y = foundRectList[0][3]

                for rect in foundRectList:
                    if rect[0] < min_x:
                        min_x = rect[0]
                    if rect[1] < min_y:
                        min_y = rect[1]
                    if rect[2] > max_x:
                        max_x = rect[2]
                    if rect[3] > max_y:
                        max_y = rect[3]
            
                self.rectangles[key] = [fitz.Rect(min_x, min_y, max_x, max_y)]
            
            #check if the correct text was found
            """
            if len(self.rectangles[key]) == 0:#key == "abstract" and self.get_text_from_bbox(self.rectangles[key][0][0],self.rectangles[key][0][1], self.rectangles[key][0][2], self.rectangles[key][0][3]):                
                textBlocks = page.getTextBlocks()
                foundRectList = [fitz.Rect(block[:4]) for block in textBlocks if get_cosine_similarity(str.lower(block[4]), str.lower(val)) > 0.7]
                #find min x, min y, max x, max y
                min_x = foundRectList[0][0]
                min_y = foundRectList[0][1]
                max_x = foundRectList[0][2]
                max_y = foundRectList[0][3]

                for rect in foundRectList:
                    if rect[0] < min_x:
                        min_x = rect[0]
                    if rect[1] < min_y:
                        min_y = rect[1]
                    if rect[2] > max_x:
                        max_x = rect[2]
                    if rect[3] > max_y:
                        max_y = rect[3]

                self.rectangles[key] = [fitz.Rect(min_x, min_y, max_x, max_y)]
            """
                
    def get_annotations(self):
        if len(self.rectangles) == 0:
            raise RectangleError("No rectangles available. Run method bbox_from_text(self) before calling this method.", "")
        
        doc = fitz.open(self.filename)
        page = doc[0]
        
        version = "4.4.0"
        flags = {}
        shapes = []
        reg = re.compile("[^/]+$")
        imagePath = re.search(reg, self.filename)[0][:-4] + ".jpeg"
        
        buffered = BytesIO()
        self.image.save(buffered, format="JPEG")
        imageDataBase64 = base64.b64encode(buffered.getvalue())
        imageData = str(imageDataBase64)[1:].replace("'","")
        
        imageHeight = self.image.height
        imageWidth = self.image.width
        
        for key, val in self.rectangles.items():
            annotation = {
                "label": key,
                "points": [],
                "group_id": None,
                "shape_type": "polygon",
                "flags": {}
            }
            
            #convert the x and y values of the rectangles
            rect_points = val[0]
            
            
            x_conversion = float(self.image.width / page.rect.width)
            y_conversion = float(self.image.height / page.rect.height)
            width = (rect_points[2] - rect_points[0]) * x_conversion
            height = (rect_points[3] - rect_points[1]) * y_conversion
            
            rect_points_converted = [
                rect_points[0] * x_conversion,
                rect_points[1] * y_conversion,
                rect_points[2] * x_conversion,
                rect_points[3] * y_conversion
            ]
            
            annotation["points"]= [
                [rect_points_converted[0], rect_points_converted[1]],
                [rect_points_converted[0] + width, rect_points_converted[1]],
                [rect_points_converted[0] + width, rect_points_converted[3]],
                [rect_points_converted[0], rect_points_converted[3]]
            ]
            shapes.append(annotation)
        annotations = {
            "version": version,
            "flags": flags,
            "shapes": shapes,
            "imagePath": imagePath,
            "imageData": imageData,
            "imageHeight": imageHeight,
            "imageWidth": imageWidth
        }
        self.annotations = annotations
        return annotations
    
    def save_annotations(self, output_path=""):
        if len(self.annotations) == 0:
            self.get_annotations()
        
        if len(output_path) != 0 and output_path[-1] != "/":
            output_path += "/"
            
        reg = re.compile("[^/]+$")
        outPath = re.search(reg, self.filename)[0][:-4] + ".json"
        with open(output_path + outPath, "w") as f:
            json.dump(self.annotations, f)
            
    def get_text_from_bbox(self, x_upper_left, y_upper_left, x_lower_right, y_lower_right):
        doc = fitz.open(self.filename)
        page = doc[0]
        """
        x_conversion = float(page.rect.width / self.image.width)
        y_conversion = float(page.rect.height / self.image.height)
        x_upper_left = (x_upper_left * x_conversion)
        y_upper_left = (y_upper_left * y_conversion)
        x_lower_right = (x_lower_right * x_conversion)
        y_lower_right = (y_lower_right * y_conversion)
        """
        rect = fitz.Rect(x_upper_left, y_upper_left, x_lower_right, y_lower_right)
        
        words = page.getText("words") # list of words on the page
        words.sort(key=lambda w: (w[3], w[0])) # ascending y, then x coordinate

        # sub-select only words that are contained INSIDE the rectangle
        #mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
        mywords = [w for w in words if fitz.Rect(w[:4]) in rect]
        group = groupby(mywords, key=lambda w: w[3])

        text = ""
        for _, gwords in group:
            text += " ".join(w[4] for w in gwords)
        return text
    
# helper_functions to compute cosine similarity between two strings
def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    word = re.compile(r'\w+')
    words = word.findall(text)
    return Counter(words)


def get_cosine_similarity(content_a, content_b):
    text1 = content_a
    text2 = content_b

    vector1 = text_to_vector(text1)
    vector2 = text_to_vector(text2)

    cosine_result = get_cosine(vector1, vector2)
    return cosine_result