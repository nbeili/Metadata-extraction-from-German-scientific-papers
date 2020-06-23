from itertools import groupby
import fitz

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
    #specify the conversion rates for x and y cordinates
    x_conversion = 1
    y_conversion = 1
    x_upper_left = x_upper_left * x_conversion
    y_upper_left = y_upper_left * y_conversion
    x_right = x_upper_left + width 
    y_right = y_upper_left + height
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
    mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
    #mywords = [w for w in words if fitz.Rect(w[:4]) in rect]
    group = groupby(mywords, key=lambda w: w[3])
    
    text = ""
    for _, gwords in group:
        text += " ".join(w[4] for w in gwords)
    print(rect)
    return text

def main():
    doc = fitz.open("11448.pdf")
    page = doc[1] # we only consider the first page of the document

    author = textfrompdf(page,207.0, 199.0,96.0,16.0,0)
    title = textfrompdf(page, 127.0,220.0,259.0,78.0)
    affiliation = textfrompdf(page, 344.0,420.0,48.0,18.0)
    date = textfrompdf(page, 149.0,470.0,239.0,18.0)
    journal = textfrompdf(page, 256.0,551.0,132.0,16.0)
    ju = textfrompdf(page, 134.0, 714.0, 169.0, 18.0)

    print("Author: {}\nAuthor: {}\naffiliation: {}\ndate: {}\njournal: {}\njournal: {}".format(author,title,affiliation,date,journal,ju))

    print("\n")
    rl1 = page.searchFor("Wissenschaftszentrum")
    rl2 = page.searchFor("Sozialforschung")
    rect = rl1[0] | rl2[0]
    
    words = page.getText("words") # list of words on the page
    words.sort(key=lambda w: (w[3], w[0])) # ascending y, then x coordinate

    mywords = [w for w in words if fitz.Rect(w[:4]) in rect]
    group = groupby(mywords, key=lambda w: w[3])

    print("Select the words strictly contained in rectangle")
    print("------------------------------------------------")
    for y1, gwords in group:
        print(" ".join(w[4] for w in gwords))  # one line
    print(rect)


if __name__ == "__main__":
    main()
