# 测试动作指令功能
#测试是否可以发送动作指令，并收到正确的动作响应。

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

    # 测试动作指令
    action_id = "4"  # 前进
    print(f"发送动作指令: action {action_id}")
    sio.emit("control_action", {"action": action_id})

    # 等待服务器响应后断开连接
    sio.sleep(5)
    sio.disconnect()
