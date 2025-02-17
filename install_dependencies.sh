#!/bin/bash

# 🚀 跨平台 Python 依賴與系統依賴安裝腳本（包含虛擬環境）
# 兼容：Ubuntu/Debian, Raspberry Pi, macOS

# 設定虛擬環境名稱
VENV_DIR="venv"

# 創建並啟動虛擬環境
setup_venv() {
    echo "🐍 設置虛擬環境 (${VENV_DIR})..."
    
    # 如果虛擬環境不存在，則創建
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        echo "✅ 虛擬環境已創建"
    fi

    # 啟動虛擬環境
    source "$VENV_DIR/bin/activate"
    echo "✅ 虛擬環境已啟動"

    # 確保 `pip` 是最新版本
    pip install --upgrade pip setuptools wheel
}

install_debian_dependencies() {
    echo "🔄 更新 Debian/Ubuntu 套件庫..."
    sudo apt-get update -y
    echo "📦 安裝系統依賴..."
    sudo apt-get install -y \
        python3-opencv libopencv-dev v4l-utils python3-pip \
        libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg \
        libgl1-mesa-glx python3-pyaudio

    # 啟動虛擬環境並安裝 Python 依賴
    setup_venv
    echo "📌 安裝 Python 依賴（來自 requirements.txt）..."
    pip install --no-cache-dir -r requirements.txt
}

install_macos_dependencies() {
    echo "🍏 檢測到 macOS，安裝 Homebrew & OpenCV..."
    
    if ! command -v brew &> /dev/null; then
        echo "⏳ 未檢測到 Homebrew，正在安裝..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    echo "📦 安裝 macOS 依賴..."
    brew install opencv portaudio ffmpeg v4l-utils

    # 啟動虛擬環境並安裝 Python 依賴
    setup_venv
    echo "📌 安裝 Python 依賴（來自 requirements.txt）..."
    pip install --no-cache-dir -r requirements.txt
}

install_raspberry_dependencies() {
    echo "🍓 檢測到 Raspberry Pi，安裝必要依賴..."
    sudo apt-get update -y
    sudo apt-get install -y \
        python3-opencv libopencv-dev v4l-utils python3-pip \
        libasound-dev portaudio19-dev libportaudiocpp0 ffmpeg
    
    # 啟動虛擬環境並安裝 Python 依賴
    setup_venv
    echo "📌 安裝 Python 依賴（來自 requirements.txt）..."
    pip install --no-cache-dir -r requirements.txt
}

main() {
    # 檢測作業系統
    case "$(uname -s)" in
        Linux*)
            if [ -f /etc/rpi-issue ]; then
                echo "🍓 檢測到 Raspberry Pi"
                install_raspberry_dependencies
            else
                echo "🐧 檢測到 Debian/Ubuntu"
                install_debian_dependencies
            fi
            ;;
        Darwin*)
            echo "🍏 檢測到 macOS"
            install_macos_dependencies
            ;;
        *)
            echo "❌ 不支持的作業系統"
            exit 1
            ;;
    esac
}

main
