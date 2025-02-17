# Intelligent Robot Terminal (Robot Side)

## 📌 Introduction

This project is the **robot-side** of the **Intelligent Robot Control System**. It runs on the **robot hardware**, executing commands received from the **[server-side (vtcfypA05)](https://github.com/Ash0Lam/vtcfypA05)**.

## 📂 Project Structure

This repository is tightly integrated with **[Server-Side (vtcfypA05)](https://github.com/Ash0Lam/vtcfypA05)**.
The roles are as follows:

### ✅ This Repository (Robot Side)

Runs on the **robot hardware**, executing movement and returning status.

**Key Features:**
- **Robot movement control** (execute commands from the server)
- **System monitoring** (report CPU temperature, battery level, and status)
- **Camera streaming** (send live video to the server)

### ✅ [Server-Side (vtcfypA05)](https://github.com/Ash0Lam/vtcfypA05)

Runs on **a PC or cloud server**, managing commands and processing requests.

**Key Features:**
- **Web control interface** (users control the robot via a webpage)
- **AI-based command processing**
- **Communicates with the robot using Socket.IO**

## 🖥️ System Requirements

### Hardware Requirements
- **Raspberry Pi / Linux Embedded Device**
- **Camera (Optional)**
- **Wi-Fi / Network Connection**

### Software Requirements
- **Python 3.12.6 (Recommended)**
- **Linux / macOS / Windows (For Development Only)**

## 📥 Installation Guide

### 1. Clone Repository

```bash
git clone https://github.com/[repository-url]
cd [repository-name]
```

### 2. Install Python

#### Ubuntu / Debian / Raspberry Pi
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```

#### macOS (Requires Homebrew)
```bash
brew install python
```

### 3. Run Installation Script

The installation script (`install_dependencies.sh`) automatically sets up all required dependencies based on your operating system. It handles:

- ✅ **Virtual Environment Setup**
  - Creates and activates a Python virtual environment
  - Updates pip, setuptools, and wheel

- ✅ **System Dependencies**
  - Ubuntu/Debian: OpenCV, v4l-utils, portaudio, ffmpeg
  - Raspberry Pi: OpenCV, v4l-utils, portaudio, ffmpeg
  - macOS: Homebrew, OpenCV, portaudio, ffmpeg, v4l-utils

- ✅ **Python Dependencies**
  - Installs all required Python packages from requirements.txt

To run the script:
```bash
chmod +x install_dependencies.sh  # Make script executable
./install_dependencies.sh         # Run installation script
```

### 4. Activate Virtual Environment

```bash
source venv/bin/activate
```

## 🏃‍♂️ How to Run

### 1. Start Robot Terminal
```bash
python robot.py
```

### 2. Configure Server Connection
When prompted, enter the IP address of the PC running the web server.

---

# 智能機器人終端 (機器人端)

## 📌 簡介

本專案是 **智能機器人控制系統的機器人端 (Robot Side)**。它運行於 **機器人設備上**，負責執行來自 **[伺服器端 (vtcfypA05)](https://github.com/Ash0Lam/vtcfypA05)** 的指令。

## 📂 專案架構

本專案與 **[伺服器端 (vtcfypA05)](https://github.com/Ash0Lam/vtcfypA05)** 緊密整合。
兩者的角色如下：

### ✅ 當前專案 (機器人端)

部署於 **機器人設備**，執行移動指令並回傳狀態。

**核心功能：**
- **機器人動作控制**（執行來自伺服器端的指令）
- **狀態監控**（回報 CPU 溫度、電池電量等）
- **即時影像串流**（將攝影機畫面傳輸到伺服器端）

### ✅ [伺服器端 (vtcfypA05)](https://github.com/Ash0Lam/vtcfypA05)

部署於 **伺服器端 (PC / 雲端)**，負責處理指令並與機器人通訊。

**核心功能：**
- **Web 控制介面**（用戶透過網頁控制機器人）
- **AI 指令解析**
- **透過 Socket.IO 與機器人溝通**

## 🖥️ 系統需求

### 硬體要求
- **樹莓派 (Raspberry Pi) / 其他 Linux 嵌入式設備**
- **攝影機 (可選)**
- **Wi-Fi / 網路連接**

### 軟體需求
- **Python 3.12.6（推薦）**
- **Linux / macOS / Windows (僅限開發)**

## 📥 安裝指南

### 1. 下載專案
```bash
git clone https://github.com/[repository-url]
cd [repository-name]
```

### 2. 安裝 Python

#### Ubuntu / Debian / 樹莓派
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```

#### macOS (需要 Homebrew)
```bash
brew install python
```

### 3. 執行安裝腳本

安裝腳本 (`install_dependencies.sh`) 會根據您的作業系統自動設置所有必要的依賴。它會執行：

- ✅ **虛擬環境設置**
  - 創建並啟動 Python 虛擬環境
  - 更新 pip、setuptools 和 wheel

- ✅ **系統依賴**
  - Ubuntu/Debian：OpenCV、v4l-utils、portaudio、ffmpeg
  - 樹莓派：OpenCV、v4l-utils、portaudio、ffmpeg
  - macOS：Homebrew、OpenCV、portaudio、ffmpeg、v4l-utils

- ✅ **Python 依賴**
  - 從 requirements.txt 安裝所有必要的 Python 套件

執行腳本：
```bash
chmod +x install_dependencies.sh  # 使腳本可執行
./install_dependencies.sh         # 執行安裝腳本
```

### 4. 啟動虛擬環境

```bash
source venv/bin/activate
```

## 🏃‍♂️ 如何啟動

### 1. 啟動機器人端
```bash
python robot.py
```

### 2. 設定伺服器連接
當提示時，輸入運行網頁伺服器的 PC 之 IP 位址。