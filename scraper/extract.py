import pdftotext

with open("source.pdf", "rb") as inFile:
    pdf = pdftotext.PDF(inFile)
    with open("new.txt", "w+") as outFile:
        outFile.write("\n#~NEWPAGE~#\n".join(pdf))
