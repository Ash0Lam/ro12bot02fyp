#测试录音转文字功能
#此测试模拟录音指令，并检查服务器是否正确返回录音结果。

import socketio

# 创建一个 Socket.IO 客户端
sio = socketio.Client()

@sio.event
def connect():
    print("成功连接到服务器！")

@sio.on("response")
def response_handler(data):
    print(f"服务器响应：{data}")

@sio.event
def disconnect():
    print("服务器已断开连接。")

if __name__ == "__main__":
    # 连接到服务器
    sio.connect('http://192.168.1.2:5000')

    # 发送录音开始指令
    print("发送录音指令")
    sio.emit("start_recording", {})

    # 等待服务器响应后断开连接
    sio.sleep(10)
    sio.disconnect()
