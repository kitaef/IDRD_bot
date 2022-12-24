import sqlite3

conn = sqlite3.connect(r'ID_RD.db')
cur = conn.cursor()
cur.execute("SELECT * FROM images WHERE image_name=='image_1';")
a = cur.fetchone()
with open('tst.jpg', 'wb') as file:
    file.write(a[3])

cur.execute("SELECT * FROM audio WHERE voice_message_name=='audio_message_4';")
a = cur.fetchone()
with open('tst.wav', 'wb') as file:
    file.write(a[3])
