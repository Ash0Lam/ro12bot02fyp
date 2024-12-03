import socketio
import wave
import pyaudio
import webrtcvad
import os
import time
import threading
import psutil
import logging
from flask import Flask
from flask_socketio import SocketIO, emit

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='robot.log',
    filemode='a'
)

# 配置参数
PC_SERVER_URL = 'http://192.168.1.30:5000'  # PC 服务器地址
ROBOT_SERVER_HOST = '0.0.0.0'  # 机器人服务器监听地址
ROBOT_SERVER_PORT = 6000       # 机器人服务器端口

# 录音参数
CHUNK = 320
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
MAX_SILENCE_FRAMES = int(RATE / CHUNK * 3)  # 3 秒静音停止录音
MAX_WAIT_FRAMES = int(RATE / CHUNK * 30)    # 最多等待 30 秒
RECORDING_PATH = "recordings"
HEARTBEAT_INTERVAL = 5  # 心跳间隔（秒）

class RobotClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.recording = False
        self.connected = False
        self.setup_socket_events()
        
        # 初始化音频设备
        self.vad = webrtcvad.Vad(2)  # 设置中等灵敏度
        self.audio = pyaudio.PyAudio()
        
        # 确保录音目录存在
        os.makedirs(RECORDING_PATH, exist_ok=True)

    def setup_socket_events(self):
        """设置 Socket.IO 事件处理"""
        @self.sio.on('connect')
        def on_connect():
            self.connected = True
            logging.info("已连接到 PC 服务器")
            self.sio.emit('robot_connect', {'type': 'robot'})

        @self.sio.on('disconnect')
        def on_disconnect():
            self.connected = False
            logging.info("与 PC 服务器断开连接")

        @self.sio.on('start_recording')
        def on_start_recording():
            if not self.recording:
                threading.Thread(target=self.record_audio).start()

        @self.sio.on('stop_recording')
        def on_stop_recording():
            self.recording = False

        @self.sio.on('play_audio')
        def on_play_audio(data):
            self.play_audio(data['file'])

        @self.sio.on('execute_action')
        def on_execute_action(data):
            self.execute_action(data['action'])

    def connect_to_server(self):
        """连接到 PC 服务器"""
        try:
            self.sio.connect(PC_SERVER_URL)
            threading.Thread(target=self.send_heartbeat, daemon=True).start()
        except Exception as e:
            logging.error(f"连接服务器失败: {e}")

    def send_heartbeat(self):
        """发送心跳包"""
        while self.connected:
            try:
                # 获取系统状态
                battery = self.get_battery_level()
                temperature = self.get_cpu_temperature()
                
                self.sio.emit('heartbeat', {
                    'status': 'active',
                    'battery': battery,
                    'temperature': temperature
                })
                logging.debug("已发送心跳包")
            except Exception as e:
                logging.error(f"发送心跳包失败: {e}")
                break
            time.sleep(HEARTBEAT_INTERVAL)

    def get_battery_level(self):
        """获取电池电量"""
        try:
            battery = psutil.sensors_battery()
            return battery.percent if battery else 100
        except:
            return 100

    def get_cpu_temperature(self):
        """获取 CPU 温度"""
        try:
            temp = psutil.sensors_temperatures()
            return temp['cpu_thermal'][0].current if 'cpu_thermal' in temp else 25
        except:
            return 25

    def record_audio(self):
        """录制音频"""
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
            
            logging.info("开始录音")

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
                    logging.error(f"录音过程中出错: {e}")
                    break

        finally:
            stream.stop_stream()
            stream.close()
            self.recording = False

        if frames and has_voice:
            self.save_and_send_audio(frames)
        else:
            logging.info("未检测到有效语音")

    def save_and_send_audio(self, frames):
        """保存并发送音频"""
        filename = os.path.join(RECORDING_PATH, f"recording_{int(time.time())}.wav")
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            logging.info(f"音频已保存: {filename}")

            # 发送音频文件
            with open(filename, 'rb') as f:
                audio_data = f.read()
                self.sio.emit('audio_upload', {
                    'filename': os.path.basename(filename),
                    'content': audio_data
                })
            logging.info("音频文件已上传")

        except Exception as e:
            logging.error(f"保存或发送音频时出错: {e}")

    def play_audio(self, audio_file):
        """播放音频文件"""
        try:
            # 如果是网络路径，需要下载文件
            if audio_file.startswith('http'):
                # 这里需要实现下载逻辑
                pass
            
            # 使用 pyaudio 播放音频
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
            
            logging.info(f"音频播放完成: {audio_file}")
            
        except Exception as e:
            logging.error(f"播放音频时出错: {e}")

    def execute_action(self, action):
        """执行动作"""
        try:
            logging.info(f"执行动作: {action}")
            
            # 这里添加实际的动作执行代码
            # 例如：调用 TonyPi 的动作控制接口
            
            # 模拟动作执行
            time.sleep(2)
            
            # 发送动作完成状态
            self.sio.emit('action_completed', {
                'action': action,
                'status': 'completed'
            })
            
            logging.info(f"动作 {action} 执行完成")
            
        except Exception as e:
            logging.error(f"执行动作时出错: {e}")
            self.sio.emit('action_completed', {
                'action': action,
                'status': 'failed',
                'error': str(e)
            })

    def cleanup(self):
        """清理资源"""
        self.recording = False
        if self.connected:
            self.sio.disconnect()
        self.audio.terminate()

def main():
    """主函数"""
    robot = RobotClient()
    
    try:
        robot.connect_to_server()
        
        # 保持程序运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序出错: {e}")
    finally:
        robot.cleanup()

if __name__ == "__main__":
    main()
