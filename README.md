# Neural_SaintPetersburg

1. Install python-telegram bot
```
pip install python-telegram-bot --pre
```
2. Install requirements (if you are using Colab)
'''
%cd stable-diffusion
pip install -r requirements.txt
'''
or create conda env (if you are running locally)
'''
conda env create -f environment.yaml
conda activate ldm
'''
3. Run
'''
python3 scripts/preload_models.py
'''
3. Create file configs.py and paste
'''
TELEGRAM_API_TOKEN = 'YOUR TOKEN'
'''
4. (Optional) Download Stable-Diffusion checkpoint
Go to https://huggingface.co/CompVis/stable-diffusion-v-1-4-original and download sd-v1-4.ckpt . Place it in models/ldm/stable-diffusion-v1

5. Run mock version of telegram bot (without stable diffusion model)
'''
python bot_main.py --mock
'''