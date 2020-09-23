# Metadata extraction from German scientific papers (PubMEX)

This repository contains  a method of extraction metadata from  German scientific papers (PDF), which have different styles and layouts, by processing the PDF as an image by using  an implementation of Detectron2 and sunthetic data of German publications. 





We used a Mask R-CNN model which is trained on COCO dataset and finetuned with
 200K converted-to-images PDFs from PubLayNet dataset. The converted PDFs include five
 basic classes (Figure, Text, etc.). Using our proposed synthetic dataset consisting of 30K
 snapshots from scientific articles, we re-finetuned the model to extract nine patterns (i.e. Title,
 Author, Abstract, etc.). We generated the proposed dataset synthetically using content in both
 English and German languages with a defined set of challenging templates acquired from
 German scientific papers. The average accuracy of our method reaches 90% which points out
 to its potential of increasing the accuracy of metadata extraction from PDF publications with
 various and challenging templates.




## Sample outputs of PubMEX
| <img src="images/21375_1036.jpeg" width=400> | <img src="images/21375_1036.jpeg" width=400> |
|---------------------------------------------------------------------------|---------------------------------------------------------------------------|
| <img src="images/11703_510.jpeg" width=400> | <img src="images/11916_950.jpeg" width=400> |
| <img src="images/12455_890.jpeg" width=400> | <img src="/images/12715_540.jpeg" width=400> |


