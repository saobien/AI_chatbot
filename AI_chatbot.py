#=======================================================
#thêm các hàm, modun
#pip install playsound==1.2.2
#pip install gtts
#pip install speechrecognition
#pip install pyinstaller
#pip install pillow
#pip install langdetect
#pip install pyaudio
#==========================================================
import queue
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import scrolledtext
import openai
import threading
from gSTT import speechtotext
from gTTS import texttospeech
import os
from time import sleep

# lấy api key trong file api_key.py
from api_key import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

# hàm lấy câu trả lời
def get_answer():
    global question, conti,regenerate
    conti = "\n"      #dùng cho viec xuong dong giữa câu hỏi và câu trả lời
    if stop_event_micro.is_set() and question=="":    #lấy câu hỏi từ ô ask_textbox khi micro tắt hoặc khi bật nhưng chưa hỏi
        question = ask_textbox.get("1.0", tk.END)
    if not stop_event_micro.is_set():
        question = ask_textbox.get("1.0", tk.END)
    regenerate = question   #biến lưu lại câu hỏi, dùng cho nút nhấn hỏi lại "regenerate_response"
    try:
        # Kiểm tra nếu nội dung không trống và không có xuống dòng
        if question.strip() :
            # Gọi hàm xử lý câu hỏi ở đây
            generate_answer(question)
        # Xóa nội dung trong ask_textbox
        ask_textbox.delete("1.0", tk.END)
        image_label.grid_remove()   #xóa hình đại diện trên cửa sổ
    except openai.OpenAIError:
        answer_textbox.delete('1.0', tk.END)
        answer_textbox.insert(tk.END, "Error: Connection failed.")
 
# hàm lấy câu trả lời từ openai
def generate_answer(question):
    global conti,answer,token_count,hang_doi
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=100,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = response['choices'][0]['message']['content']    #nội dung câu trả lời lưu vào biến answer dùng cho việc hiển thị
        hang_doi.put(answer)                                     #luu vào biến hang_doi dùng cho viec đọc ra loa
        token_count=response['usage']['completion_tokens']       #lấy số lượng tokens của câu trả lời để quản lí việc tự động trả lời tiếp
        answer_textbox.delete('1.0', tk.END)
        answer_textbox.insert(tk.END, question + conti)
        answer_textbox.insert(tk.END, answer)
    except:
        answer = ""

#hàm kiểm tra xuống dòng trong lúc nhập vào ô ask_textbox
def check_shift_key(event):
    if event.state & 1 != 0 and event.keysym == "Return":  # Kiểm tra phím Shift+Enter
        return
    if event.keysym == "Return":
        get_answer()

# 2 hàm dùng cho việc tự động trả lời tiếp khi nội dung quá dài
def check_and_display_continue():
    global check_thread
    # Kiểm tra xem số lượng token có vượt quá giới hạn max_tokens hay không   
    if stop_event_check.is_set():
        stop_event_check.clear()
        stop_conti_button.config(text="Continue generating")
        micro_label.config(text="AI chatbot:...waiting for your questions...")

    else:
        stop_event_check.set()
        check_thread = threading.Thread(target=continue_generating)
        check_thread.start()
        stop_conti_button.config(text="Stop generating")
        
def continue_generating(max_tokens=100):
    global conti,token_count,chatbot
    lan = 0
    while stop_event_check.is_set():
        print(token_count)
        if token_count==max_tokens:
            lan = 0
            conti = ""
            question = answer_textbox.get('1.0', tk.END).strip()
            if question:
                answer_textbox.mark_set(tk.INSERT, tk.END)  # Đặt vị trí con trỏ tại cuối textbox
                chatbot="AI chatbot:...to be continue,waiting 5s..."
                #sleep(20)
                generate_answer(question)
        else:
            if lan<5:
                chatbot="AI chatbot:...waiting for your questions..."
                lan+=1
    chatbot="AI chatbot:...waiting for your questions..."            
    token_count = 0
    print("da thoat continue")

#hàm dùng cho việc hỏi lại câu hỏi đã ghi trước đó
def regenerate_response():
    print(regenerate)
    try:
        if regenerate.strip() :
            generate_answer(regenerate)
    except openai.OpenAIError:
        answer_textbox.delete('1.0', tk.END)
        answer_textbox.insert(tk.END, "Error: Connection failed.")

#2 hàm dùng điều khiển mic, cập nhật câu hỏi từ micro
def micro():
    global speech_thread,question,chatbot
    question=""
    if stop_event_micro.is_set():
        stop_event_micro.clear()
        micro_button.config(bg="orange")
        chatbot="AI chatbot:...micro turn off..."
    else:
        stop_event_micro.set()
        speech_thread = threading.Thread(target=update_question)
        speech_thread.start()
        micro_button.config(bg="cyan")
        chatbot="AI chatbot:...waiting for your questions..."

def update_question(max_tokens=100):
    global question,token_count,chatbot
    while stop_event_micro.is_set():
        if token_count<max_tokens or not stop_event_check.is_set():    #đang tự động trả lời tiếp nội dung thì không nghe
            question = speechtotext()
            if question!="":
                chatbot="--->"+question
                get_answer()
                question=""
            else:
                chatbot="AI chatbot:...waiting for your questions..."
        else:
            chatbot="AI chatbot:...to be continue,waiting 5s..."
    print("đã thoát mic")          

#2 hàm dùng cho việc phát câu trả lời ra loa
def speaker():
    global speaker_thread,hang_doi
    if stop_event_speaker.is_set():
        stop_event_speaker.clear()
        speaker_button.config(bg="orange")

    else:
        stop_event_speaker.set()
        speaker_thread = threading.Thread(target=update_answer)
        speaker_thread.start()
        speaker_button.config(bg="cyan")
        while not hang_doi.empty():
            hang_doi.get()
        if answer != "":
            hang_doi.put(answer)

def update_answer():
    temp1=""
    while stop_event_speaker.is_set():
        if not hang_doi.empty():
            temp = hang_doi.get()
            texttospeech(temp)
            sleep(5)
    print("đã thoát speaker")  
#----------------------------------------------------------------------------------
# Code cho nút Exit và nút Close
#----------------------------------------------------------------------------------
# Code thoát ứng dụng            
def quit_app():
    stop_event_check.clear()
    stop_event_speaker.clear()
    stop_event_micro.clear()

    #xoá các file tạm phát sinh trong quá trình chương trình làm việc 
    filelist = [ f for f in os.listdir('temp/') if f.endswith(".mp3") ]
    for f in filelist:
        os.remove(os.path.join('temp/', f)) 
    window.destroy()
   
# Xử lý khi nút "Close" được nhấn
def handle_close():
    quit_app()

#hàm dùng cập nhật nội dung thông báo của AI chatbot
def update_micro_label():
    micro_label.config(text=chatbot)
    window.after(1500, update_micro_label)

#hàm khởi tạo giao diện
def interface():
    # Khai báo biến toàn cục
    global window, answer_textbox, ask_textbox, send_button, regenerate_button, stop_conti_button
    global micro_button,speaker_button,micro_label,photo,image_label

    # Khởi tạo cửa sổ giao diện
    window = tk.Tk()
    window.title("AI chatbot")

    # Đăng ký hàm xử lý khi cửa sổ đóng
    window.protocol("WM_DELETE_WINDOW", handle_close)

    # Đặt kích thước mặc định cho cửa sổ
    window.geometry("600x600")  # Thay đổi kích thước theo nhu cầu của bạn
    window.configure(bg="light green")  # Đặt màu nền của cửa sổ là màu đen
    
    try:
        # Lấy đường dẫn thư mục của script hiện tại
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Đường dẫn tới tệp tin icon (ví dụ: icon.ico) tương đối với thư mục hiện tại
        icon_filename = "AI.ico"
        icon_path = os.path.join(current_dir, icon_filename)

        # Kiểm tra xem tệp tin icon có tồn tại không
        if os.path.exists(icon_path):
            # Đặt biểu tượng cho cửa sổ nếu tệp tin icon tồn tại
            window.iconbitmap(icon_path)
    except:
        pass
    # Định dạng cửa sổ ứng dụng đầy khung cửa sổ
    for i in range(9):
        window.grid_columnconfigure(i, weight=1)
        window.grid_rowconfigure(i, weight=1)

    # ScrolledText hiển thị câu hỏi và câu trả lời
    answer_textbox = scrolledtext.ScrolledText(window,font=("Arial", 14), wrap=tk.WORD, height=20)
    answer_textbox.grid(row=0,rowspan=5,column=0, columnspan=9, sticky="nsew")

    # thanh trạng thái khi dùng mic
    micro_label = tk.Label(window, text=chatbot)
    micro_label.grid(row=5, column=0, columnspan=9, sticky="nsew")
    
    # Nút stop/continue generating
    stop_conti_button = tk.Button(window, text="Continue Generating", command=check_and_display_continue)
    stop_conti_button.grid(row=6,column=4, columnspan=1,sticky="nsew" )

    # Nút regenerate response
    regenerate_button = tk.Button(window, text="Regenerate Response", command=regenerate_response)
    regenerate_button.grid(row=6, column=5, columnspan=1,sticky="nsew" )

    # Khung nhập câu hỏi
    ask_textbox = scrolledtext.ScrolledText(window, font=("Arial", 12), wrap=tk.WORD, height=2)
    ask_textbox.grid(row=10, rowspan=2, column=0, columnspan=7, sticky="nsew")
    ask_textbox.bind("<Key>",  lambda event:check_shift_key(event))
   
    # Nút micro
    micro_button = tk.Button(window,bg="orange",text="Micro", command=micro)
    micro_button.grid(row=10,rowspan=1, column=7, columnspan=1, sticky="nsew") 

    # Nút speaker
    speaker_button = tk.Button(window,bg="orange",text="Speaker", command=speaker)
    speaker_button.grid(row=10,rowspan=1, column=8, columnspan=1, sticky="nsew") 

    # Nút gửi
    send_button = tk.Button(window,text="Send", command=get_answer)
    send_button.grid(row=11,rowspan=1, column=7, columnspan=1, sticky="nsew")

    # Nút thoát
    exit_button = tk.Button(window,text="Exit", command=quit_app)
    exit_button.grid(row=11,rowspan=1, column=8, columnspan=1, sticky="nsew")

    # thanh trạng thái
    status_label = tk.Label(window, text="Code By: Trần Quốc Minh, giáo viên Trường THPT Văn Hiến")
    status_label.grid(row=12, column=0, columnspan=9, sticky="nsew")

    # Đường dẫn tới bức hình
    image_path = "AI.png"

    # Đọc bức hình từ tệp tin
    image = Image.open(image_path)

    # Điều chỉnh kích thước bức hình (nếu cần)
    image = image.resize((300, 300))

    # Tạo đối tượng PhotoImage từ bức hình
    photo = ImageTk.PhotoImage(image)

    # Tạo widget Label để chứa bức hình và đặt bức hình vào đó
    image_label = tk.Label(window,bg="white", image=photo)
    image_label.grid(row=1,rowspan=3, column=3, columnspan=3, sticky="nsew")

#=========================================================================================
#phần chương trình chính
#=========================================================================================
#khởi tạo các giá trị ban đầu

regenerate = ""
question = ""
answer = ""
token_count = 0
conti = "\n"
chatbot="AI chatbot:...micro turn off..."
stop_event_micro = threading.Event()      #sự kiện cho đa luồng
stop_event_speaker = threading.Event()
stop_event_check = threading.Event()
speech_thread = None
speaker_thread = None
check_thread = None 
hang_doi = queue.Queue()   # Tạo hàng đợi

# tạo giao diện
interface()
# Cập nhật nhãn micro_label khi biến chatbot thay đổi
update_micro_label()
# Chạy vòng lặp chính
window.mainloop()