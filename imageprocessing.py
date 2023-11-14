import pytesseract
from PIL import Image
from io import BytesIO
import database
from config import server_side

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"


async def parse_image(message: dict) -> str:
    if (
        message.attachments
        and message.content
        and message.content[:5].lower() == "!snip"
    ):
        for attachment in message.attachments:
            if attachment.width and attachment.height:
                image_raw = await attachment.read()
                image = Image.open(BytesIO(image_raw))
                print(image)
                if server_side:
                    print("server_side boolean")
                    pytesseract.pytesseract.tesseract_cmd = (
                        r"/home/grixus/froakbot/.venv/bin/pytesseract"
                    )

                extracted_text = pytesseract.image_to_string(image)
                print("Extracted Text:", extracted_text)
                database_results = await database.parse_image(extracted_text)
                await message.channel.send(database_results)
                return
