import socketio
import wave
import pyaudio
import webrtcvad
import os
import time
import threading

# WebSocket 客戶端
sio = socketio.Client()

# 配置参数
SERVER_URL = 'http://192.168.1.2:5000'  # 替换为 PC 的 IP 地址
CHUNK = 320  # 每幀數據大小
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
MAX_SILENCE_FRAMES = int(RATE / CHUNK * 3)  # 3 秒靜音停止錄音
MAX_WAIT_FRAMES = int(RATE / CHUNK * 30)   # 最多等待 30 秒
OUTPUT_FILE = "robot_recording.wav"
HEARTBEAT_INTERVAL = 5  # 心跳包发送间隔（秒）

# 初始化 PyAudio 和 WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(2)  # 中等靈敏度


def start_recording():
    """录音并上传到服务器"""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    silence_count = 0
    has_voice = False

    print("[INFO] 开始录音，等待语音触发...")

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)

            if vad.is_speech(data, RATE):
                frames.append(data)
                silence_count = 0
                has_voice = True
                print("[INFO] 检测到语音，录音中...")
            else:
                silence_count += 1

            if has_voice and silence_count > MAX_SILENCE_FRAMES:
                print("[INFO] 静音超过 3 秒，结束录音")
                break

            if not has_voice and len(frames) > MAX_WAIT_FRAMES:
                print("[INFO] 超过 30 秒无语音，结束等待")
                break
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    if frames:
        with wave.open(OUTPUT_FILE, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        print(f"[INFO] 录音保存为 {OUTPUT_FILE}")
        send_audio_to_pc(OUTPUT_FILE)
    else:
        print("[INFO] 无有效录音，重新开始")


def send_audio_to_pc(audio_file):
    """将录音文件上传到服务器"""
    if os.path.exists(audio_file):
        try:
            with open(audio_file, 'rb') as f:
                sio.emit('audio_upload', {'filename': audio_file, 'content': f.read()})
            print("[INFO] 录音文件已上传至服务器")
        except Exception as e:
            print(f"[ERROR] 上传录音文件失败: {e}")
    else:
        print("[ERROR] 录音文件不存在")


def play_audio(audio_file):
    """播放来自服务器的音频"""
    if os.path.exists(audio_file):
        try:
            wf = wave.open(audio_file, 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(CHUNK)
            while data:
                stream.write(data)
                data = wf.readframes(CHUNK)
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"[ERROR] 播放音频文件失败: {e}")
    else:
        print("[ERROR] 音频文件不存在，无法播放")


def send_heartbeat():
    """定期发送心跳包"""
    while True:
        try:
            sio.emit('heartbeat', {'status': 'active'})
            print("[INFO] 心跳包已发送")
        except Exception as e:
            print(f"[ERROR] 心跳包发送失败: {e}")
            break
        time.sleep(HEARTBEAT_INTERVAL)


@sio.on('tts_audio')
def handle_tts_audio(data):
    """接收 TTS 音频文件并播放"""
    audio_file = data.get('audio_file', 'response.wav')
    try:
        with open(audio_file, 'wb') as f:
            f.write(data['content'])
        print("[INFO] 已接收并保存 TTS 音频，准备播放...")
        play_audio(audio_file)
    except Exception as e:
        print(f"[ERROR] 接收 TTS 音频失败: {e}")


@sio.on('control_action')
def handle_control_action(data):
    """接收动作指令并执行"""
    action = data.get("action")
    if action:
        print(f"[INFO] 接收到动作指令: {action}")
        execute_action(action)
        # 发送动作完成消息
        sio.emit('action_response', {'status': 'done', 'action': action})
    else:
        print("[ERROR] 接收到无效的动作指令")


def execute_action(action):
    """执行机械人动作"""
    print(f"[INFO] 执行动作: {action}")
    time.sleep(2)  # 模拟动作时间
    print(f"[INFO] 动作 {action} 执行完成")


@sio.event
def connect():
    print("[INFO] 已连接到服务器")
    # 启动心跳线程
    threading.Thread(target=send_heartbeat, daemon=True).start()


@sio.event
def disconnect():
    print("[INFO] 与服务器断开连接")


if __name__ == '__main__':
    try:
        print("[INFO] 正在连接到服务器...")
        sio.connect(SERVER_URL)
        while True:
            start_recording()
    except KeyboardInterrupt:
        print("[INFO] 程序终止")
    except Exception as e:
        print(f"[ERROR] 连接到服务器失败: {e}")
