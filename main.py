
import subprocess
import sqlite3
import io
import numpy as np
import cv2
import mediapipe as mp
from aiogram import Bot, Dispatcher, executor, types


# Please put your bot token here: 
API_TOKEN = ''
 
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Connect to a database
conn = sqlite3.connect(r'ID_RD.db')
cur = conn.cursor()
cur.execute(
            'CREATE TABLE IF NOT EXISTS audio\
            (user_id INTEGER,\
            voice_message_name TEXT,\
            voice_message_id TEXT,\
            voice_message_bytes BLOB);'
            )
cur.execute(
            'CREATE TABLE IF NOT EXISTS images\
            (user_id INTEGER,\
            image_name TEXT,\
            image_id TEXT,\
            image_bytes BLOB);'
            )

mp_face_detection = mp.solutions.face_detection

def convert_oga_wav(src_filename, dst_filename):
      process = subprocess.run(['ffmpeg', '-y', '-i', src_filename, '-ar', '16000', dst_filename])

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
   await message.reply("Hello!\nI am IDRD bot.\n Send me a message, a voice note, or a picture.")
   print('message received')

# Handler for voice notes
@dp.message_handler(content_types=types.ContentType.VOICE)
async def audio_handler(message: types.Message):
   '''If there is a voice note in a message, function downloads it by id,
   converts to 16 kHz wav file and saves to a database'''

   uid = message.from_id
   file_id = message.voice.file_id
   input_file_name = 'input_file.oga'
   await bot.download_file_by_id(file_id, destination=input_file_name)
   await message.answer(f'I received a voice note with {message.voice.duration} seconds duration\nNow it is being processed.')
   convert_oga_wav(input_file_name, dst_filename="output.wav")
   with open('output.wav', 'rb') as audio_bytes:
      file_bytes = audio_bytes.read()
   # Count actual number of audio messages saved in the database for current user
   cur_user_audio_count = cur.execute(f'SELECT COUNT(*) FROM audio WHERE user_id=={uid};').fetchone()[0]
   file_name = 'audio_message_' + str(cur_user_audio_count)
   cur.execute(
               f'INSERT INTO audio (user_id, voice_message_name, voice_message_id, voice_message_bytes) VALUES (?,?,?,?);',
               (uid, file_name, file_id, file_bytes)
               )
   conn.commit()
   await message.answer(f'Your audio message is saved to a database')
   print('audio received')

# Handler for images and detecting faces
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def picture_handler(message: types.Message):
   '''Checks if there are human faces in the image and saves the image
   to the database if faces are detected.'''

   uid = message.from_id
   file_id = message.photo[-1].file_id
   image_bytes = io.BytesIO()
   await bot.download_file_by_id(file_id, destination=image_bytes)
   # Prepare data for processing without saving to a file
   content = image_bytes.getvalue()
   np_array = np.frombuffer(content, np.uint8)
   img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)     
   img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
   # Detect faces in the image
   with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
      results = face_detection.process(img)
      print(f'faces found: {len(results.detections) if results.detections else 0}')
      if results.detections:
         # Count actual number of images saved in the database for current user
         cur_user_image_count = cur.execute(f'SELECT COUNT(*) FROM images WHERE user_id=={uid};').fetchone()[0]
         file_name = 'image_' + str(cur_user_image_count)
         cur.execute(
                     f'INSERT INTO images (user_id, image_name, image_id, image_bytes) VALUES (?,?,?,?);',
                     (uid, file_name, file_id, content)
                     )
         conn.commit(
         )
         num_faces = len(results.detections)
         await message.answer(f'Number of faces detected on the picture: {num_faces}. Your picture have been saved to database')
      else:
         await message.answer(f'No faces detected, your picture have NOT been saved to database')

@dp.message_handler()
async def echo(message: types.Message):
   await message.answer('Hello, I am ID R&D bot.\nYou can send me a voice note or a picture, and it will be saved into a database')
   print('message received')
 
if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)
