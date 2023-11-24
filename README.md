# froakbot
###### A Discord bot for Everquest (an MMORPG)

The discord bot parses a snip of the character names in a zone:

![alt text](https://cdn.discordapp.com/attachments/617825237752479751/1175861016316358656/image.png?ex=656cc4e8&is=655a4fe8&hm=064098870915b8f663045b87ebcfa378e0cafa5d5a14762bdc3cd8ca84e5a3d7&)

And returns the class composition of the characters:

![alt_text](https://cdn.discordapp.com/attachments/617825237752479751/1175861244234842284/image.png?ex=656cc51f&is=655a501f&hm=f479a9c521b3195c50a2e8e91af8ab2d8e9b432f80a659a84e784d1093860bfa&)

The bot parses the image and compares the character names to a SQLite database (created by hand). Red highlight = Enemy, Blue highlight = Friendly.

Also contains basic CRUD commands for search of character data.

# Dev Notes:

Created in Python. The bot reads / writes to a local SQLite database. The image parsing library used is Pytesseract.
