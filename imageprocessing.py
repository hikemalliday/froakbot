import pytesseract
from PIL import Image
from io import BytesIO
import database
from config import tesseract

pytesseract.pytesseract.tesseract_cmd = tesseract


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

                extracted_text = pytesseract.image_to_string(image)
                await database.parse_image(extracted_text, message)
                return
