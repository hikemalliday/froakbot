# import mysql.connector
server_side = False
allowed_roles = ["Brain Trust", "Admin", "Froak", "Members"]
guilds = ["Tempest", "Pumice", "Sanctuary", "Serenity", "Guildless"]
url = "http://45.55.129.24:8004/post_message"

if server_side:
    # tesseract = r"/usr/bin/tesseract"
    db_path = "/home/grixus/froakbot/froak-db/master.db"
    # mysql_connection = mysql.connector.connect(
    #     host="127.0.0.1", user="root", password="froakbot1328!", database="froakbot"
    # )
else:
    # tesseract = r"C:\Program Files\Tesseract-OCR\tesseract"
    db_path = "./froak-db/master.db"
    # mysql_connection = mysql.connector.connect(
    #     host="127.0.0.1", user="root", password="froakbot1328!", database="froakbot"
    # )
