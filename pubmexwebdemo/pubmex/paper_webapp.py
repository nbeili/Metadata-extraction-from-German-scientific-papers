from pubmex.paper import *

class Paper_webapp(Paper):
     def __init__(self, file, metadata_dict, metadata_page=0):
        
        self.file = file
        self.image = self.to_image()
        self.metadata = metadata_dict
        self.rectangles = {}
        self.annotations = []