
![unware-bot](https://i.ibb.co/8D50yCqc/photo-5400011374685451857-c.jpg)

# > unware bot

# ᐳ Description  
> Telegram bot and web backend for GTA models & textures database.  
>  
> Features:  
> * Converts `.bpc` files -> `.zip`  
> * Converts `.mod` files <-> `.dff`  
> * Website with full models list and “get” button  
> * Separate admin site to edit models list  
> * Stores data in JSON files  
> * Uses kram and pvrttextoolcli for texture conversions (legacy)

# ᐳ Setup  
> * Clone the repo:  
> `git clone https://github.com/psychobye/unware-bot.git && cd unware-bot`  
> * Install dependencies:  
> `pip install -r requirements.txt`  
> * Edit `config.py` — add your Telegram API token and admin/chat IDs

# ᐳ Linux users must  
> * Install kram from [release](https://github.com/alecazam/kram/releases/download/v1.7.30/kram-linux.zip)  
> * Unzip, place the binary somewhere convenient  
> * Update `KRAM_PATH` and `PVRTEXTOOL_PATH` in `config.py`

# ᐳ Run  
> `python main.py`

# ᐳ Notes  
> * No hardcoded paths except in `config.py`  
> * Async and efficient processing  
> * JSON-based storage for models and skins  
> * Web frontend for users and admins

# ᐳ TODO  
> - [ ] BTX converter (Windows & Linux)  
> - [ ] Anti-spam
