import speech_recognition as sr
#import pyaudio
# hàm chuyển giọng nói thành văn bản
speech_text = ""
def speechtotext():
    global speech_text
    robot_ear = sr.Recognizer()
    for i in range(1):                  # nghe ??? lần để tăng khả năng tiếp nhận thông tin, tùy nhập vào range()
        with sr.Microphone() as mic:
            print("AI chatbot: ...đang lắng nghe... ")
            audio = robot_ear.adjust_for_ambient_noise(mic)
            audio = robot_ear.listen(mic,phrase_time_limit=10)
            robot_ear.pause_threshold=1.5        
            try:
                TEXT = robot_ear.recognize_google(audio,language="vi-VI")
                print(f"Bạn:...{TEXT}...")
                TEXT=TEXT.lower()
                speech_text = TEXT
            except:                         # không có phản hồi thì text là rỗng
                speech_text =''
    return  speech_text
# hàm dùng để test hàm chuyển giọng nói thành văn bản
'''
def main():       
    speech_text=speechtotext()
    print('Bạn (ALL TEXT):...' ,speech_text)
# thực hiện hàm test
if __name__=="__main__":
    while True:
        main()
'''