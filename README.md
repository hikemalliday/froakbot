# froakbot
###### A Discord bot for Everquest (an MMORPG)

##### Docker Hub:
[https://hub.docker.com/repository/docker/hikemalliday/froakbot/general](https://hub.docker.com/repository/docker/hikemalliday/froakbot/general)

The discord bot parses a snip of the character names in a zone:

![alt text](https://cdn.discordapp.com/attachments/617825237752479751/1175861016316358656/image.png?ex=656cc4e8&is=655a4fe8&hm=064098870915b8f663045b87ebcfa378e0cafa5d5a14762bdc3cd8ca84e5a3d7&)

And returns the class composition of the characters:

![alt_text](https://cdn.discordapp.com/attachments/617825237752479751/1175861244234842284/image.png?ex=656cc51f&is=655a501f&hm=f479a9c521b3195c50a2e8e91af8ab2d8e9b432f80a659a84e784d1093860bfa&)

The bot parses the image and compares the character names to a SQLite database (created by hand). Red highlight = Enemy, Blue highlight = Friendly.

Also contains basic CRUD commands for search of character data.

# Dev Notes:

Created in Python. The bot reads / writes to a local SQLite database. The image parsing library used is Pytesseract.
I built it so that my guildmates can assess the class composition of an enemy force, before charging into battle (we play on a PvP server).

I find that Discord.Py (the library I used to create the bot) is quite easy to dev with. The Discord API is easy to use. I get a lot of personal value / use out of this bot, as do my guildmates.

#### Upon reflection:

My initial thought process was, modulize all the function that interact with the database into their own file. Hence, 'database.py'. Well, almost all the methods interact with the database! Therefor, it would a poor choice / naming scheme. I intend to add more features to this bot eventually, and I will refactor the mehods / modules at that time.
