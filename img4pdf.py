import img2pdf
import zipfile
import sys

zip_path = sys.argv[1]

with zipfile.ZipFile(zip_path) as archive:
    images=[]
    for item in archive.infolist():
        if item.is_dir():
            continue

        if item.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            images.append(item)

    images.sort(key=lambda item: item.filename)

    image_data = [
        archive.read(item)
        for item in images
    ]
    
    with open ("Конспект.pdf", "wb") as output:
        output.write(img2pdf.convert(*image_data))