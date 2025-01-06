import socketio
import wave
import pyaudio
import webrtcvad
import os
import time
import threading
import psutil
import logging
import re
from flask import Flask
from flask_socketio import SocketIO, emit
import importlib.util
import json
import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='robot.log',
    filemode='a'
)

# 配置文件路徑
CONFIG_FILE = "robot_config.json"

def load_last_server_address():
    """讀取上次的服務器地址"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('last_server_address')
    except:
        return None

def save_server_address(address):
    """保存服務器地址"""
    try:
        config = {'last_server_address': address}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"保存配置失敗: {e}")

# 嘗試導入 ActionGroupDict
try:
    spec = importlib.util.spec_from_file_location(
        "ActionGroupDict", 
        "./TonyPi/ActionGroupDict.py"
    )
    action_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(action_module)
    ACTION_GROUP_DICT = action_module.action_group_dict
    print("[INFO] 成功載入動作組字典")
except Exception as e:
    print(f"[WARNING] 無法載入動作組字典: {e}")
    ACTION_GROUP_DICT = {
        "0": "揮手",
        "1": "前進",
        "2": "後退",
        "3": "左轉",
        "4": "右轉",
        "9": "測試動作"
    }

def validate_ip_and_port(ip_address):
    """驗證IP地址和端口格式"""
    pattern = r'^http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'
    match = re.match(pattern, ip_address)
    
    if not match:
        return False
    
    # 驗證IP地址
    ip_parts = match.group(1).split('.')
    for part in ip_parts:
        if not 0 <= int(part) <= 255:
            return False
    
    # 驗證端口
    port = int(match.group(2))
    if not 0 <= port <= 65535:
        return False
    
    return True

def get_server_address():
    """獲取服務器地址"""
    last_address = load_last_server_address()
    
    while True:
        print("\n請輸入PC服務器地址")
        print("格式: http://IP:PORT")
        print("例如: http://192.168.1.30:5000")
        if last_address:
            print(f"直接按 Enter 使用上次的地址: {last_address}")
        
        server_address = input("服務器地址: ").strip()
        
        # 如果直接按 Enter 且有上次的地址，使用上次的地址
        if not server_address and last_address:
            print(f"\n使用上次的地址: {last_address}")
            return last_address
            
        # 如果輸入了新地址，驗證格式
        if not server_address:
            continue
            
        if validate_ip_and_port(server_address):
            save_server_address(server_address)
            print(f"\n正在連接到服務器: {server_address}")
            return server_address
        else:
            print("\n錯誤: 無效的地址格式，請使用 http://IP:PORT 格式")

# 獲取用戶輸入的服務器地址
PC_SERVER_URL = get_server_address()

# 配置参数
ROBOT_SERVER_HOST = '0.0.0.0'       # 機器人服務器監聽地址
ROBOT_SERVER_PORT = 6000            # 機器人服務器端口

# 錄音參數
CHUNK = 320
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
MAX_SILENCE_FRAMES = int(RATE / CHUNK * 3)  # 3 秒靜音停止錄音
MAX_WAIT_FRAMES = int(RATE / CHUNK * 30)    # 最多等待 30 秒
RECORDING_PATH = "recordings"
HEARTBEAT_INTERVAL = 10  # 心跳間隔（秒）

class RobotClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.recording = False
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # 重連延遲（秒）
        self.setup_socket_events()
        
        # 初始化音頻設備
        self.vad = webrtcvad.Vad(2)  # 設置中等靈敏度
        self.audio = pyaudio.PyAudio()
        
        # 確保錄音目錄存在
        os.makedirs(RECORDING_PATH, exist_ok=True)
        
        # 打印可用動作列表
        print("\n可用的動作列表:")
        for key, value in ACTION_GROUP_DICT.items():
            print(f"動作 {key}: {value}")

    def setup_socket_events(self):
        """設置 Socket.IO 事件處理"""
        @self.sio.on('connect')
        def on_connect():
            self.connected = True
            self.reconnect_attempts = 0
            logging.info("已連接到 PC 服務器")
            self.sio.emit('robot_connect', {'type': 'robot'})
            print("成功連接到服務器，開始發送心跳...")

        @self.sio.on('disconnect')
        def on_disconnect():
            self.connected = False
            logging.info("與 PC 服務器斷開連接")
            threading.Thread(target=self.connection_monitor, daemon=True).start()


        @self.sio.on('start_recording')
        def on_start_recording():
            if not self.recording:
                threading.Thread(target=self.record_audio).start()

        @self.sio.on('stop_recording')
        def on_stop_recording():
            self.recording = False

        @self.sio.on('play_audio')
        def on_play_audio(data):
            """接收音频数据并播放"""
            audio_file = data.get('file')
            audio_data = data.get('audio_data')
        
            if audio_data:
                # 如果接收到音频数据，则直接播放它
                self.play_audio_from_data(audio_data)
            elif audio_file:
                # 如果是文件路径，直接从文件播放
                self.play_audio(audio_file)
        
        def play_audio_from_data(self, audio_data):
            """从音频数据播放音频"""
            try:
                # 使用 pyaudio 播放二进制音频数据
                stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True
                )
        
                # 播放音频数据
                stream.write(audio_data)
                stream.stop_stream()
                stream.close()
        
                logging.info("音频播放完成")
            except Exception as e:
                logging.error(f"播放音频时出错: {e}")


        @self.sio.on('execute_action')
        def on_execute_action(data):
            self.execute_action(data['action'])

    def connection_monitor(self):
        """監控連接狀態"""
        while not self.connected and self.reconnect_attempts < self.max_reconnect_attempts:
            print(f"\n嘗試重新連接 ({self.reconnect_attempts + 1}/{self.max_reconnect_attempts})...")
            if self.connect_to_server():
                break
            time.sleep(self.reconnect_delay)
        
        if not self.connected:
            print("\n無法重新連接到服務器，請檢查網絡連接或重啟程序")

    def connect_to_server(self):
        """連接到 PC 服務器"""
        try:
            self.sio.connect(PC_SERVER_URL)
            threading.Thread(target=self.send_heartbeat, daemon=True).start()
            return True
        except Exception as e:
            self.reconnect_attempts += 1
            logging.error(f"連接服務器失敗: {e}")
            return False

    def send_heartbeat(self):
        """發送心跳包"""
        while self.connected:
            try:
                battery = self.get_battery_level()
                temperature = self.get_cpu_temperature()
                
                heartbeat_data = {
                    'status': 'active',
                    'battery': battery,
                    'temperature': temperature,
                    'timestamp': time.time()
                }
                
                self.sio.emit('heartbeat', heartbeat_data)
                print("發送心跳包...")  # 添加這行來確認心跳正在發送
                logging.info("已發送心跳包")
            except Exception as e:
                logging.error(f"發送心跳包失敗: {e}")
                if not self.connected:
                    break
            time.sleep(HEARTBEAT_INTERVAL)

    def get_battery_level(self):
        """獲取電池電量"""
        try:
            battery = psutil.sensors_battery()
            return battery.percent if battery else 100
        except:
            return 100

    def get_cpu_temperature(self):
        """獲取 CPU 溫度"""
        try:
            temp = psutil.sensors_temperatures()
            return temp['cpu_thermal'][0].current if 'cpu_thermal' in temp else 25
        except:
            return 25

    def record_audio(self):
        """錄製音頻"""
        self.recording = True
        frames = []
        silence_count = 0
        has_voice = False

        try:
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            logging.info("開始錄音")

            while self.recording:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    if self.vad.is_speech(data, RATE):
                        frames.append(data)
                        silence_count = 0
                        has_voice = True
                    else:
                        silence_count += 1
                        if has_voice:
                            frames.append(data)

                    if has_voice and silence_count > MAX_SILENCE_FRAMES:
                        break

                    if not has_voice and len(frames) > MAX_WAIT_FRAMES:
                        break

                except Exception as e:
                    logging.error(f"錄音過程中出錯: {e}")
                    break

        finally:
            stream.stop_stream()
            stream.close()
            self.recording = False

        if frames and has_voice:
            self.save_and_send_audio(frames)
        else:
            logging.info("未檢測到有效語音")

    def save_and_send_audio(self, frames):
        """保存並發送音頻"""
        filename = os.path.join(RECORDING_PATH, f"recording_{int(time.time())}.wav")
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            logging.info(f"音頻已保存: {filename}")

            if self.connected:  # 只在連接狀態下發送
                # 發送音頻文件
                with open(filename, 'rb') as f:
                    audio_data = f.read()
                    self.sio.emit('audio_upload', {
                        'filename': os.path.basename(filename),
                        'content': audio_data
                    })
                logging.info("音頻文件已上傳")
            else:
                logging.warning("未連接到服務器，無法上傳音頻")

        except Exception as e:
            logging.error(f"保存或發送音頻時出錯: {e}")

    def play_audio(self, audio_file):
        """播放音頻文件"""
        try:
            # 如果是網絡路徑，需要下載文件
            if audio_file.startswith('http'):
                # 這裡需要實現下載邏輯
                pass
            
            # 使用 pyaudio 播放音頻
            wf = wave.open(audio_file, 'rb')
            stream = self.audio.open(
                format=self.audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )

            data = wf.readframes(CHUNK)
            while data:
                stream.write(data)
                data = wf.readframes(CHUNK)

            stream.stop_stream()
            stream.close()
            wf.close()
            
            logging.info(f"音頻播放完成: {audio_file}")
            
        except Exception as e:
            logging.error(f"播放音頻時出錯: {e}")

    def execute_action(self, action):
        """執行動作"""
        try:
            action_name = ACTION_GROUP_DICT.get(str(action), "未知動作")
            logging.info(f"執行動作: {action} ({action_name})")
            print(f"\n[執行動作] {action_name}")
            
            # 真實機器人動作執行
            try:
                from .HiwonderSDK.Board import Board
                from .HiwonderSDK.ActionGroupControl import ActionGroupControl
                
                # 初始化並執行動作
                Board.setBusServoPulse(19, 500, 500)  # 示例：控制舵機
                AGC = ActionGroupControl()  # 動作組控制
                AGC.runActionGroup(action)   # 運行動作組
                
                print(f"正在執行動作：{action_name}")
                
            except ImportError:
                print("無法導入 HiwonderSDK，使用模擬模式")
                time.sleep(1)  # 模擬動作執行時間
            
            # 發送完成狀態
            if self.connected:
                self.sio.emit('action_completed', {
                    'action': action,
                    'name': action_name,
                    'status': 'completed'
                })
            
            logging.info(f"動作 {action_name} 執行完成")
            
        except Exception as e:
            error_msg = f"執行動作時出錯: {e}"
            logging.error(error_msg)
            if self.connected:
                self.sio.emit('action_completed', {
                    'action': action,
                    'name': action_name,
                    'status': 'failed',
                    'error': error_msg
                })

    def cleanup(self):
        """清理資源"""
        print("\n正在關閉連接...")
        self.recording = False
        if self.connected:
            try:
                self.sio.disconnect()
            except:
                pass
        self.audio.terminate()

def main():
    """主函數"""
    robot = RobotClient()
    
    try:
        if not robot.connect_to_server
