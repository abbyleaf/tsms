from pdf2image import convert_from_path
import os

for filename in (x.name for x in os.scandir('./all') if x.is_file()):
    print(filename)
    filepath = './all/' + filename
    filename = filename.split('.')[0]
    convert_from_path(filepath, output_folder='./converted',
                      fmt='png', output_file=filename)
