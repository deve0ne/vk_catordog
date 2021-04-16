import requests, io
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message, 'random_id': 0})


def recognition(img_bytes):
    from keras.models import load_model
    from keras.preprocessing import image
    import numpy as np
    from PIL import Image

    model = load_model('new_model.h5')

    img = Image.open(io.BytesIO(img_bytes))
    img = img.convert('RGB')
    target_size = (150, 150)
    img = img.resize(target_size)
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.

    prediction = model.predict(img_tensor)
    return prediction


token, _, group_id = open('config.txt', "r").read().split(" ")

vk = vk_api.VkApi(token=token)

longpoll = VkBotLongPoll(vk, group_id)

# Основной цикл
for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object["message"]
        peer_id = msg["peer_id"]

        try:
            attach1 = msg["attachments"][0]
            try:
                photo = attach1["photo"]
                photo_url = photo["sizes"][2]["url"]
            except:
                write_msg(peer_id, "Прикреплённый файл не является фото")
                continue
        except:
            write_msg(peer_id, "Вы не прикрепили фото")
            continue

        response = requests.get(photo_url)
        byte_img = response.content

        prediction = recognition(byte_img)
        prediction = str(prediction).replace('[', '').replace(']', '')
        prediction = float(prediction) * 100

        if prediction > 50:
            write_msg(
                peer_id, "Я уверен на {0:.1f}%, что это собака".format(prediction))
        else:
            write_msg(peer_id, "Я уверен на {0:.1f}%, что это кошка".format(100 - prediction))
