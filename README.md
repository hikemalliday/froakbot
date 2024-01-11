# froakbot
###### A Discord bot for Everquest (an MMORPG)

##### Docker Hub:
[https://hub.docker.com/repository/docker/hikemalliday/froakbot/general](https://hub.docker.com/r/hikemalliday/froakbot)

The discord bot parses an image of the character names in a zone:

![alt text](https://cdn.discordapp.com/attachments/617825237752479751/1175861016316358656/image.png?ex=656cc4e8&is=655a4fe8&hm=064098870915b8f663045b87ebcfa378e0cafa5d5a14762bdc3cd8ca84e5a3d7&)

And returns the class composition of the characters:

![alt_text](https://cdn.discordapp.com/attachments/1180635913022353499/1181287913418407946/image.png?ex=65808319&is=656e0e19&hm=94fc1307646a55001c7c82673b9eabdcdaa16470cadb8449ae38c8f3dd7121f4&)

The bot parses the image and compares the character names to a SQLite database (created by hand). Red highlight = Enemy, Blue highlight = Friendly.

Also contains basic CRUD commands for search of character data.

# Dev Notes:

Currently re-vamping the database (migrating tables and such) for a better naming convention, added FKs, and also so I can scale the bot into a raid attendence / loot tracker.

I created a simple [website](https://github.com/hikemalliday/froakbot-website-frontend) that displays all of the discord bots output, in an endless scroll page.

Created in Python. The bot reads / writes to a local SQLite database. The image parsing library used is Pytesseract.
I built it so that my guildmates can assess the class composition of an enemy force, before charging into battle (we play on a PvP server).

I find that Discord.Py (the library I used to create the bot) is quite easy to dev with. The Discord API is easy to use. I get a lot of personal value / use out of this bot, as do my guildmates.


