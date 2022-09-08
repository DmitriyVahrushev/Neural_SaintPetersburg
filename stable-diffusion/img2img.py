# https://colab.research.google.com/drive/1dGYi0HTl_Il3MBFLTc78DckiMieRr-s1?usp=sharing

from diffusers import StableDiffusionImg2ImgPipeline, preprocess
from torch import autocast
import torch

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_img2img_model(token):
    """token from https://huggingface.co/docs/transformers/model_sharing"""

    torch.cuda.empty_cache()
    
    model = StableDiffusionImg2ImgPipeline.from_pretrained(
        "models/ldm/stable-diffusion-v1-4",
        revision="fp16",
        torch_dtype=torch.float16,
        use_auth_token=token,
    )

    return model


def img2img(input_text: str,
            input_img: str,
            width: int = 512,
            height: int = 512,
            seed: int = 42 , 
            strength: float = 0.45, 
            guidance: float = 14.0,
            model):

    torch.cuda.empty_cache()

    # load model
    model.to(DEVICE)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(int(seed))

    # preprocess image
    copy = input_img.copy()
    copy = copy.resize((int(width), int(height)))
    init_image = preprocess(copy)

    with autocast(DEVICE):
        image = model(
            prompt=input_text,
            init_image=init_image,
            generator=gen,
            strength=strength,
            guidance_scale=guidance,
        )["sample"]

    return image[0]
