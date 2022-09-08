from ldm.simplet2i import T2I

try:
    model = T2I(
        embedding_path='logs/kazan_cathedral_5122022-09-06T20-49-43_my_key/checkpoints/embeddings_gs-3999.pt'
    )
    model.load_model()
except: # TODO: add precise exception for missing checkpoint file
    model = None
# t2i = T2I(
#     weights='./models/ldm/stable-diffusion-v1/model.ckpt',
#     config='./configs/stable-diffusion/v1-inference.yaml',
#     sampler_name='ddim',
#     embedding_path='./models/embeddings.pt'  # modify the embedding path
# )
# t2i.load_model()


def generate_image(text_prompt:str):
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
    outputs = model.txt2img(text_prompt)
    img_path = outputs[0][0]
    return img_path