# froakbot
###### A Discord bot for Everquest (an MMORPG)

##### Docker Hub:
[https://hub.docker.com/repository/docker/hikemalliday/froakbot/general](https://hub.docker.com/r/hikemalliday/froakbot)

##### Currently undergoing a refactor that will allow me to write some assertions (under the guidance of a senior dev friend of mine)

Froakbot is not only a DKP / Loot tracking bot, but also has an image parsing feature that returns data about the game state.

### Image Parser:

The discord bot parses an image of the character names in a zone:

![alt text](https://cdn.discordapp.com/attachments/617825237752479751/1175861016316358656/image.png?ex=656cc4e8&is=655a4fe8&hm=064098870915b8f663045b87ebcfa378e0cafa5d5a14762bdc3cd8ca84e5a3d7&)

And returns the class composition of the characters:

![alt_text](https://cdn.discordapp.com/attachments/1180635913022353499/1181287913418407946/image.png?ex=65808319&is=656e0e19&hm=94fc1307646a55001c7c82673b9eabdcdaa16470cadb8449ae38c8f3dd7121f4&)

The bot parses the image and compares the character names to a SQLite database (created by hand). Red highlight = Enemy, Blue highlight = Friendly.

Also contains basic CRUD commands for search of character data.

### Database architecture:

![alt_text](https://cdn.discordapp.com/attachments/1180635913022353499/1197241520181485708/image.png?ex=65ba8d0e&is=65a8180e&hm=431f1b2bbc59cdc0ff7f39cb92e64e19bc88167d82b6c9e80ee28e5d6b12f8f1&)

# Dev Notes:

I created a simple [website](https://github.com/hikemalliday/froakbot-website-frontend) that displays all of the discord bots output, in an endless scroll page.

I created 'items_master' by copying a few columns from the Project Quarm items table, so that when awarding raid loot, when you input the item_name string, if spelled close enough, it will enter the correct spelling of the item into the database. This allows for standardized data that is more queryable. 'items_master' also contains a column called 'icon', which is a number that maps an item's in game image to an image file. I scraped all of the item image files from the P99 wiki, using my own [webscraper](https://github.com/hikemalliday/p99wiki-scraper), and the images are correctly mapped with the correct ID's. This will allow me to returnn a nice looking 'card' in Discord that will show a picture of the item when loot is awarded.

All of the CRUD commands are reading and writing from duplicate 'test' tables I created, because I am currently undergoing heavy work on this project.

Created in Python. The bot reads / writes to a local SQLite database. The image parsing library used is Pytesseract.
I built it so that my guildmates can assess the class composition of an enemy force, before charging into battle (we play on a PvP server).

I find that Discord.Py (the library I used to create the bot) is quite easy to dev with. The Discord API is easy to use. I get a lot of personal value / use out of this bot, as do my guildmates.


