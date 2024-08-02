# IMPORTANT INFO!
This is made for the raspberry pi 5 and most likely will ***not*** work on other platforms. However, this is free to be used and changed for your own needs.

# Instructions To use:
1. Set up your own bot at https://discord.com/developers. You can find many a helpful walkthroughs online. 
2. Create a file called key.env in the same folder as the ServerManager&period;py file.
3. Include in the file two lines:
    1. TOKEN="Your Bot's Token"
    2. GUILD="Your Discord Server's ID"
4. Use the [Raspberry Pi Terraria Server Install Guide](https://terraria.wiki.gg/wiki/Server#How_to_%28RPI_/_Others_OSes%29) and move the files needed into the same folder as used for this repo (So the software can stay up to date).
5. Move the terrariad file to /usr/local/bin and replace YOURUSERNAME with your username.
6. Move the terraria.service file to /etc/systemd/system after replacing all the important uppercase blocks with the relative information.
7. Run the discord bot and type /sync in the discord server. 
8. Type /start in the discord server and now the Terraria Server should be running.
