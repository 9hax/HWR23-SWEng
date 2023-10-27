from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader, PdfWriter
import os

def addText(documentFileName: str, outputFileName: str, pageModificationList: list) -> None:
    ''' This function adds text to a PDF document.
    To add text to a PDF, the following parameters are needed:

    documentFile: file -> This is a python file handle (usually created using open()) to the source PDF.
    outputFileName: str -> This is the path to a location where the modified PDF will be saved.
    pageModificationList: list -> This is a list of the modifications made to the PDF file.

    The pageModificationList has the following format:
    Every object in the modification list is another list, representing the page the modification is on.
    Every page list is a list of text objects that should be placed on the page. 
    Every text Object is a dictionary containing the keys 'text', 'x' and 'y'.
    
    Example: 
      addText('test.pdf', 'output.pdf', [[{'text':"Hello World",'x':0,'y':0}]])
    
    This adds the text "Hello World" to the bottom left corner of the Page. 
    '''
    pageNumber = 0
    for modificationList in pageModificationList:
        with open(outputFileName + "_overlay_" + str(pageNumber) + ".pdf", 'wb') as canvasFile:
            c = Canvas(canvasFile)
            for modification in modificationList:
                c.drawString(modification['x'] * 596, modification['y'] * 842, modification['text'])
            c.save()
        pageNumber += 1
    output = PdfWriter()
    with open(documentFileName, 'rb') as documentFile:
        document = PdfReader(documentFile)
        for documentPageNumber in range(len(document.pages)):
            page = document.pages[documentPageNumber]
            try:
                with open(outputFileName + "_overlay_" + str(documentPageNumber) + ".pdf", 'rb') as dataFile:
                    data = PdfReader(dataFile)
                    page.merge_page(data.pages[0])
                    output.add_page(page)
            except FileNotFoundError:
                pass
        with open(outputFileName, 'wb') as output_file:
            output.write(output_file)
    for overlayNumber in range(0, pageNumber):
        filename = outputFileName + "_overlay_" + str(overlayNumber) + ".pdf"
        if os.path.exists(filename):
            os.remove(filename)


