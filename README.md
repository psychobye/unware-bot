# unware-bot

telegram bot + web backend for gta models & textures database.

what it does:  
- converts `.bpc` files to `.zip`  
- converts `.mod` files to `.dff` and back  
- website with full models list + “get” button  
- separate admin site to edit models list  
- stores data in json files  
- uses kram & pvrttextoolcli for texture conversions (old)

setup:  
clone repo:  
`git clone https://github.com/psychobye/unware-bot.git && cd unware-bot`  
install deps:  
`pip install -r requirements.txt`  
edit `config.py` — add your telegram api token, admin/chat ids

**linux users must:**  
- install kram from https://github.com/alecazam/kram/releases/download/v1.7.30/kram-linux.zip  
- unzip, put binary somewhere, update `KRAM_PATH` in `config.py`  
- update `PVRTEXTOOL_PATH` too  

run:  
`python main.py`

notes:  
- no hardcoded paths except in `config.py`   
- async and efficient processing  
- json based storage for models & skins  
- web frontend for users and admins  

## TODO
- btx converter (win & linux)
- anti-spam