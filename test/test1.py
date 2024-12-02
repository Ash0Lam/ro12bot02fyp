#测试文字输入功能
#测试是否可以发送文字输入，并收到服务器响应。

import socketio

# 创建一个 Socket.IO 客户端
sio = socketio.Client()

@sio.event
def connect():
    print("成功连接到服务器！")

@sio.on("response")
def response_handler(data):
    print(f"服务器响应：{data}")  # 打印从服务器收到的响应

@sio.event
def disconnect():
    print("服务器已断开连接。")

if __name__ == "__main__":
    # 连接到服务器
    sio.connect('http://192.168.1.2:5000')

    # 发送文字输入测试
    test_text = "你好，這是一個測試文字"
    print(f"发送文字输入: {test_text}")
    sio.emit("text_input", {"text": test_text})

    # 等待服务器响应后断开连接
    sio.sleep(5)
    sio.disconnect()
