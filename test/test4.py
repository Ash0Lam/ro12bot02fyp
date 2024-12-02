#心跳测试

import socketio
import time

# 初始化 Socket.IO 客户端
sio = socketio.Client()

# 服务器地址（替换为实际的服务器 IP 和端口）
SERVER_URL = "http://192.168.1.2:5000"  # 替换 <PC_IP> 为服务器实际 IP 地址

# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 5  # 每 5 秒发送一次心跳


@sio.event
def connect():
    print("[INFO] 已连接到服务器")
    # 开始发送心跳信号
    send_heartbeat()


@sio.event
def disconnect():
    print("[INFO] 与服务器断开连接")


@sio.on('heartbeat_response')
def handle_heartbeat_response(data):
    """处理服务器的心跳响应"""
    print(f"[INFO] 收到心跳响应: {data}")


def send_heartbeat():
    """定期发送心跳信号到服务器"""
    while True:
        try:
            sio.emit('heartbeat', {'status': 'alive', 'timestamp': time.time()})
            print("[INFO] 发送心跳信号")
            time.sleep(HEARTBEAT_INTERVAL)  # 每隔指定时间发送一次
        except Exception as e:
            print(f"[ERROR] 发送心跳失败: {e}")
            break


if __name__ == '__main__':
    try:
        # 连接到服务器
        sio.connect(SERVER_URL)
        sio.wait()  # 保持连接
    except Exception as e:
        print(f"[ERROR] 无法连接到服务器: {e}")
