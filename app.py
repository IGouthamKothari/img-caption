from flask import Flask, request, jsonify, render_template
from transformers import AutoProcessor, BlipForConditionalGeneration, AutoTokenizer
import torch
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# object of processor,model,tokenizer
processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/blip-image-captioning-base")

# Setting for the Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)



def generate_caption(image):
    max_length = 16
    num_beams = 1  # Generating only one caption
    gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

    i_image = Image.open(image)  # opening and storing image in i_image variable
    if i_image.mode != "RGB":  # Checking if image is in RGB, if not then convert it to RGB
        i_image = i_image.convert(mode='RGB')

    img = [i_image]  # Creating a list with a single image

    # Extracting the pixel values
    pixel_val = processor(images=img, return_tensors="pt").pixel_values
    pixel_val = pixel_val.to(device)

    # Generating output using pretrained model
    output = model.generate(pixel_val, **gen_kwargs)

    # Converting output of model to text
    caption = tokenizer.batch_decode(output, skip_special_tokens=True)
    caption = caption[0].strip()  # Extracting the caption from the list

    return caption


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image found in the request'})

        image = request.files['image']
        caption = generate_caption(image)

        result = {'caption': caption}
        return jsonify(result)

    return render_template('indexold.html')


if __name__ == '__main__':
    app.run()
