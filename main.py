import os
import time
from io import BytesIO

import openai as openai
import pytesseract
from PIL import ImageGrab, Image

###DEFINE###
lang = "eng"
api_key = "sk-..."
model = "gpt-3.5-turbo"
chatgpt_use = True
############

tesseract_path = "C:\\Program Files\\Tesseract-OCR"
pytesseract.pytesseract.tesseract_cmd = os.path.join(tesseract_path, 'tesseract.exe')

openai.api_key = api_key

def get_image_from_clipboard():
    try:
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            return img
        else:
            return None
    except:
        return None

def chat_gpt_request(ocr_text):
    prompt = f"Please correct any errors in the following OCR extracted text and format it as code if it's a code snippet, the result must be the md encoded text:\n\n{ocr_text}\n"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

previous_png_image_data = None
query_counter = 0

while True:
    image = get_image_from_clipboard()

    if image:
        if image.format != 'PNG':
            image = image.convert('RGBA')
            with BytesIO() as output:
                image.save(output, format='PNG')
                png_image_data = output.getvalue()
        else:
            with BytesIO() as output:
                image.save(output, format='PNG')
                png_image_data = output.getvalue()

        if png_image_data != previous_png_image_data:
            previous_png_image_data = png_image_data
            image = Image.open(BytesIO(png_image_data))
            sample_text = pytesseract.image_to_string(image, lang='eng')
            print(sample_text)

            if(chatgpt_use):
                chat_gpt_response = chat_gpt_request(sample_text)
            else:
                chat_gpt_response = "ChatGPT usage was turned off"

            query_counter += 1
            image_filename = f'pictures\\query_{query_counter}_image.png'
            image.save(image_filename)

            with open('output.md', 'a', encoding='utf-8') as md_file:
                md_file.write(f'![Query {query_counter} Image]({image_filename})\n\n')
                md_file.write(f'OCR: {sample_text}\n\n')
                md_file.write(f'Chat: \n{chat_gpt_response}\n\n')
                md_file.write('---\n\n')
        else:
            print("No new image found in clipboard.")
    else:
        print("No image found in clipboard.")

    input("Press ENTER to continue, or Ctrl + C to exit...")