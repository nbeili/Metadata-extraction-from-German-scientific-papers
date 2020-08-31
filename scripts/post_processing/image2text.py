from itertools import groupby


def tensor_to_text(tensor, pdf_filename, metadataCatalog):
    """
    Computes the text in a pdf file corresponding to each bounding box that was detected in the image of the PDF

    :tensor: the tensor containing the detected bounding boxes and segmentations for the image corresponding to the PDF
    :pdf_filename: path to the actual pdf document
    :metadataCatalog: detectron2 metadataCatalog that contains the information about the class labels
    :return: dictionary of the class labels as keys and the corresponding text as value
    """

    results = {}

    

def textfrompdf(page, x_upper_left, y_upper_left, width, height, margin=0.0):
    """
    Inputs: 
        page -> a page of a pdf document (can be retrieved like this:
            doc = fitz.open("filename")
            page = doc[page]
        )
        x_upper_left --> the x-cordinate of the upper left corner of the bbox
        x_upper_left --> the y-cordinate of the upper left corner of the bbox
        width --> the width of the bbox
        height --> the height of the bbox

    Output:
        String --> the words contained inside the bbox
    """
    # Define the rectangle
    #####################################
    # SOME OF OUR MANUAL ANNOTATIONS ARE INACCURATE --> add a margin to include all text that we want
    # we should think about removing this if our annotations are correct
    #####################################
    margin = 3

    #specify the conversion rates for x and y cordinates
    x_conversion = float(page.rect.width / 596)
    y_conversion = float(page.rect.height / 794)
    x_upper_left = (x_upper_left * x_conversion) - margin
    y_upper_left = (y_upper_left * y_conversion) - margin
    x_right = x_upper_left + (width * x_conversion) + margin
    y_right = y_upper_left + (height * y_conversion) + margin
    rect = fitz.Rect(x_upper_left,y_upper_left,x_right, y_right)

    """
    Get all words on page in a list of lists. Each word is represented by:
    [x0, y0, x1, y1, word, bno, lno, wno]
    The first 4 entries are the word's rectangle coordinates, the last 3 are just
    technical info (block number, line number, word number).
    The term 'word' here stands for any string without space.
    """

    words = page.getText("words") # list of words on the page
    words.sort(key=lambda w: (w[3], w[0])) # ascending y, then x coordinate

    # sub-select only words that are contained INSIDE the rectangle
    #mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
    mywords = [w for w in words if fitz.Rect(w[:4]) in rect]
    group = groupby(mywords, key=lambda w: w[3])
    
    text = ""
    for _, gwords in group:
        text += " ".join(w[4] for w in gwords)
    print(rect)
    return text
