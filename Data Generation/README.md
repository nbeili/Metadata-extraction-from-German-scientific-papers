
Execute the script files according to this sequence:

1). Generate new data: First SAVE from your template the first page (or the relevant page which has metadata), then convert it to docx file. Place both the docx and PDF file 
in the folder containing 'Generating new data.ipynb' and 'Convert docx to PDFs.ipynb' . Check the layout of the docx file and replace the data (e.g author name, title etc) 
with data from your dataframe. This will generate docx files for new generated data 

2). Convert docx files to PDFs. 'Convert docx to PDFs.ipynb' will automatically create new folder 'PDFs'. Place 'Convert PDFs to Images and Resize.ipynb' and 
'Annotating Generated data.ipynb' in this folder. 

3). Then Convert PDFs to images and resize them

4). Annotate images. If image is not annotated, you may need to check whether the bounding boxes list, coordinates_author list, coordinates_title list and so on are empty or not. 


P.S. "dataframe_engabstract" has abstracts with english translations while "dataframe_gerabstract" has only german abstracts
