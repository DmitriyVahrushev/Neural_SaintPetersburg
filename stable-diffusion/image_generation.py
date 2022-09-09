from ldm.simplet2i import T2I

try:
    model = T2I(
        embedding_path='fin_embeddings/embedding.pt'
    )
    model.load_model()
except FileNotFoundError:
    print('Some checkpoints files are missing. Model isn\'t loaded')
    model = None

# t2i = T2I(
#     weights='./models/ldm/stable-diffusion-v1/model.ckpt',
#     config='./configs/stable-diffusion/v1-inference.yaml',
#     sampler_name='ddim',
#     embedding_path='./models/embeddings.pt'  # modify the embedding path
# )
# t2i.load_model()


def generate_image(text_prompt:str, init_img_path=None):
    # results = t2i.prompt2image(
    #     prompt   = text_prompt,
    #     outdir   = "./outputs/",
    #     iterations=1,
    #     steps=50
    # )
    # save the image in outputs folder
    # for row in results:
    #     im   = row[0]
    #     seed = row[1]
    #     im.save(f'./outputs/image-{seed}.png')
    if model is None:
        return 'misc/test_img.jpg'
    if init_img_path:
        outputs = model.txt2img(text_prompt, init_img=init_img_path)
    else:
        outputs = model.txt2img(text_prompt)
    img_path = outputs[0][0]
    return img_path