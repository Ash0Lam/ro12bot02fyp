ï¿¼
1
23456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120121122123124125126127593594595596597598599600601602603604605606607608609610611612613614615616617618619620621622623624625626627628629630631632633634635636637638639640641642643644645646647648649650651652653654655656657658659660661662663664665666
import socketio
import wave
# import pyaudio
import webrtcvad
import os
import time
import threading
import psutil
import logging
import re
import cv2
import base64
from flask import Flask
from flask_socketio import SocketIO, emit
import importlib.util
import json
import datetime

# éç½®æ¥å¿
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='robot.log',
    filemode='a'
)

# éç½®æä»¶è·¯å¾
CONFIG_FILE = "robot_config.json"

def load_last_server_address():
    """è®€åä¸æ¬¡çæåå¨å°å€"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('last_server_address')
    except:
        return None

def save_server_address(address):
    """ä¿å­æåå¨å°å€"""
    try:
        config = {'last_server_address': address}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"ä¿å­éç½®å¤±æ: {e}")

# åè©¦å°å¥ ActionGroupDict
try:
    spec = importlib.util.spec_from_file_location(
        "ActionGroupDict", 
        "./TonyPi/ActionGroupDict.py"
    )
    action_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(action_module)
    ACTION_GROUP_DICT = action_module.action_group_dict
    print("[INFO] æåè¼å¥åä½çµå­å¸")
except Exception as e:
    print(f"[WARNING] ç¡æ³è¼å¥åä½çµå­å¸: {e}")
    ACTION_GROUP_DICT = {
        "0": "æ®æ",
        "1": "åé€²",
        "2": "å¾é€€",
        "3": "å·¦è½",
        "4": "å³è½",
        "9": "æ¸¬è©¦åä½"
    }

def validate_ip_and_port(ip_address):
    """é©è­IPå°å€åç«¯å£æ ¼å¼"""
    pattern = r'^http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'
    match = re.match(pattern, ip_address)
    
    if not match:
        return False
    
    # é©è­IPå°å€
    ip_parts = match.group(1).split('.')
    for part in ip_parts:
        if not 0 <= int(part) <= 255:
            return False
    
    # é©è­ç«¯å£
    port = int(match.group(2))
    if not 0 <= port <= 65535:
        return False
    
    return True

def get_server_address():
    """ç²åæåå¨å°å€"""
    last_address = load_last_server_address()
    
    while True:
        print("\nè«è¼¸å¥PCæåå¨å°å€")
        print("æ ¼å¼: http://IP:PORT")
        print("ä¾å¦: http://192.168.1.30:5000")
        if last_address:
            print(f"ç´æ¥æ Enter ä½¿ç¨ä¸æ¬¡çå°å€: {last_address}")
        
        server_address = input("æåå¨å°å€: ").strip()
        
        # å¦æç´æ¥æ Enter ä¸æä¸æ¬¡çå°å€ï¼ä½¿ç¨ä¸æ¬¡çå°å€
        if not server_address and last_address:
            print(f"\nä½¿ç¨ä¸æ¬¡çå°å€: {last_address}")
            return last_address
            
        # å¦æè¼¸å¥äºæ°å°å€ï¼é©è­æ ¼å¼
        if not server_address:
            continue
            
        if validate_ip_and_port(server_address):
            save_server_address(server_address)
            print(f"\næ­£å¨é€£æ¥å°æåå¨: {server_address}")
            return server_address
        else:
            print("\né¯èª¤: ç¡æçå°å€æ ¼å¼ï¼è«ä½¿ç¨ http://IP:PORT æ ¼å¼")

# ç²åç¨æ¶è¼¸å¥çæåå¨å°å€
PC_SERVER_URL = get_server_address()

# éç½®åæ°
ROBOT_SERVER_HOST = '0.0.0.0'       # æ©å¨äººæåå¨ç£è½å°å€
ROBOT_SERVER_PORT = 6000            # æ©å¨äººæåå¨ç«¯å£

# éé³åæ¸
CHUNK = 320
            
            # çå¯¦æ©å¨äººåä½å·è¡
            try:
                from .HiwonderSDK.Board import Board
                from .HiwonderSDK.ActionGroupControl import ActionGroupControl
                
                # åå§åä¸¦å·è¡åä½
                Board.setBusServoPulse(19, 500, 500)  # ç¤ºä¾ï¼æ§å¶èµæ©
                AGC = ActionGroupControl()  # åä½çµæ§å¶
                AGC.runActionGroup(action)   # éè¡åä½çµ
                
                print(f"æ­£å¨å·è¡åä½ï¼{action_name}")
                
            except ImportError:
                print("ç¡æ³å°å¥ HiwonderSDKï¼ä½¿ç¨æ¨¡æ¬æ¨¡å¼")
                time.sleep(1)  # æ¨¡æ¬åä½å·è¡æé
            
            # ç¼é€å®æç€æ
            if self.connected:
                self.sio.emit('action_completed', {
                    'action': action,
                    'name': action_name,
                    'status': 'completed'
                })
            
            logging.info(f"åä½ {action_name} å·è¡å®æ")
            
        except Exception as e:
            error_msg = f"å·è¡åä½æåºé¯: {e}"
            logging.error(error_msg)
            if self.connected:
                self.sio.emit('action_completed', {
                    'action': action,
                    'name': action_name,
                    'status': 'failed',
                    'error': error_msg
                })

    def cleanup(self):
        """æ¸çè³æº"""
        print("\næ­£å¨ééé€£æ¥...")
        self.recording = False
        if self.connected:
            try:
                self.sio.disconnect()
            except:
                pass
        # ä»¥ä¸ä»£ç å·²æ³¨é
        # self.audio.terminate()

def main():
    """ä¸»å½æ¸"""
    robot = RobotClient()
    
    try:
        if not robot.connect_to_server():
            print("ç¡æ³é€£æ¥å°æåå¨ï¼ç¨åºå°é€€åº")
            return

        # ä¿æä¸»ç·ç¨éè¡ï¼ç´å°ç¨æ¶ä¸­æ·
        try:
            while robot.connected:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\næ¶å°ä¸­æ·ä¿¡èï¼æ­£å¨éé...")

    except Exception as e:
        print(f"ç¼çæªé æçé¯èª¤: {e}")
    
    finally:
        robot.cleanup()

if __name__ == "__main__":
    main()
