from unidecode import unidecode

lines = []

f = open("new.txt", "r")

number = 1
title = True

for line in f:
    if '#~NEWPAGE~#' in line:
        title = True
    elif title:
        line = str(number) + " " + line.upper()
        number += 1
        title = False
        line = unidecode(line).strip()
        lines.append(line)
        lines.append("")
    else:
        line = unidecode(line).strip()
        lines.append(line)

with open("final.txt", "w+") as outFile:
    outFile.write("\n".join(lines))
