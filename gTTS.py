from gtts import gTTS
from langdetect import detect
import time
from playsound import playsound
import re

# Hàm chuyển văn bản thành giọng nói
def texttospeech(TEXT):
    language_support = ["af", "sq", "ar", "hy", "bn", "ca", "zh", "zh-cn", "zh-tw", "zh-yue", "hr", "cs", "da", "nl", "en", "en-au", "en-uk", "en-us", "eo", "fi", "fr", "de", "el", "hi", "hu", "is", "id", "it", "ja", "km", "ko", "la", "lv", "mk", "no", "pl", "pt", "ro", "ru", "sr", "si", "sk", "es", "es-es", "es-us", "sw", "sv", "ta", "th", "tr", "uk", "vi", "cy"]
    try:
        pattern = r'^[0-9,.]+$'
        match = re.match(pattern, TEXT)
        if match:
            detected_language = "vi"
        else:
            detected_language = detect(TEXT)
            if not detected_language in language_support:
                detected_language = "en"
        robot_speech = gTTS(TEXT,lang=detected_language,slow=False)  # chuyển văn bản thành giọng nói
        timestamp = str(int(time.time()))
        file= 'temp/ai_' + timestamp + '.mp3'                 #đặt tên file mp3
        robot_speech.save(file)                         #lưu file mp3
        playsound(file)                                # mở file mp3
    except:
        playsound('mp3/is_connect.mp3')
        print("Không có kết nối")                       # thông báo ko có kết nối mạng trên màn hình

# hàm này dùng để test hàm chuyển văn bản thành giọng nói
'''
def main():
    texttospeech("""Bài hát: Múa cho mẹ xem.
                Hai bàn tay của em, tay em múa cho mẹ xem.
                Hai bàn tay của em...như hai con bướm xinh thật xinh.
                Khi em đưa tay lên...là bướm xinh bay múa.
                Khi em đưa tay xuống...là con bướm đậu trên cành hồng""")
# thực hiện hàm main() để test
if __name__=="__main__":
    main()
'''