server_side = True

if server_side:
    tesseract = r"/usr/bin/tesseract"
    db_path = "/home/grixus/froakbot/froak-db/master.db"
else:
    tesseract = r"C:\Program Files\Tesseract-OCR\tesseract"
    db_path = "./froak-db/master.db"
