## NOTE: No longer active

# froakbot
###### A Discord bot for Everquest (an MMORPG)

##### Docker Hub:
[https://hub.docker.com/repository/docker/hikemalliday/froakbot/general](https://hub.docker.com/r/hikemalliday/froakbot)

Froakbot is not only a DKP / Loot tracking bot, but also has an image parsing feature that returns data about the game state.

### Image Parser:

The discord bot parses an image of the character names in a zone:

![alt text](https://cdn.discordapp.com/attachments/617825237752479751/1175861016316358656/image.png?ex=656cc4e8&is=655a4fe8&hm=064098870915b8f663045b87ebcfa378e0cafa5d5a14762bdc3cd8ca84e5a3d7&)

And returns the class composition of the characters:

![alt_text](https://cdn.discordapp.com/attachments/1180635913022353499/1181287913418407946/image.png?ex=65808319&is=656e0e19&hm=94fc1307646a55001c7c82673b9eabdcdaa16470cadb8449ae38c8f3dd7121f4&)

The bot parses the image and compares the character names to a SQLite database (created by hand). Red highlight = Enemy, Blue highlight = Friendly.

Also contains basic CRUD commands for search of character data.

### Database architecture:

![alt_text](https://cdn.discordapp.com/attachments/617825237752479751/1201295363911467179/image.png?ex=65c94c7d&is=65b6d77d&hm=9e5c1cab26d4619ef03439e47b26ab538da8e13ec47e1ae53bbbb285c49633aa&)

# Dev Notes:

I created a GitHub Action (workflow YAML) that triggers on commit to master branch:

The action writes the SSH private key that I have stored in secrets to a text file 'id_rsa'. This 'id_rsa' file is stored in the 'runner' for the workflow file, which to my best knowledge is either a container or a VM that is spun up on githubs server. We then change the mode of said file to read and write, append the return from 'ssh-keyscan <server ip>' to a text file called 'known_hosts'. Next, we SSH login to my server and execute a shell script file that stops a linux 'service' (froakbot), runs 'git pull', then starts the 'service'.

![alt_text](https://cdn.discordapp.com/attachments/617825237752479751/1200078638004048022/image.png?ex=65c4df53&is=65b26a53&hm=724cc9e52f3d17844092ef24d699feb12ec44485dd56eca08e12136985729399&)

I created a simple [website](https://github.com/hikemalliday/froakbot-website-frontend) that displays all of the discord bots output, in an endless scroll page.

I created 'items_master' by copying a few columns from the Project Quarm items table, so that when awarding raid loot, when you input the item_name string, if spelled close enough, it will enter the correct spelling of the item into the database. This allows for standardized data that is more queryable. 'items_master' also contains a column called 'icon', which is a number that maps an item's in game image to an image file. I scraped all of the item image files from the P99 wiki, using my own [webscraper](https://github.com/hikemalliday/p99wiki-scraper), and the images are correctly mapped with the correct ID's. This will allow me to returnn a nice looking 'card' in Discord that will show a picture of the item when loot is awarded. 

EXAMPLE:

![alt_text](https://cdn.discordapp.com/attachments/1180635913022353499/1197943947759194192/image.png?ex=65bd1b3d&is=65aaa63d&hm=2c326fa092438f82e91e5a21e2da8364b91c82246af77b7f929a44a2025675a0&)

All of the CRUD commands are reading and writing from duplicate 'test' tables I created, because I am currently undergoing heavy work on this project.

Created in Python. The bot reads / writes to a local SQLite database. The image parsing library used is Pytesseract.
I built it so that my guildmates can assess the class composition of an enemy force, before charging into battle (we play on a PvP server).

I find that Discord.Py (the library I used to create the bot) is quite easy to dev with. The Discord API is easy to use. I get a lot of personal value / use out of this bot, as do my guildmates.


