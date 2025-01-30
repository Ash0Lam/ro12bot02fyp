#!/bin/bash

# 跨平台依賴安裝腳本

install_debian_dependencies() {
    sudo apt-get update
    sudo apt-get install -y \
        python3-opencv \
        libopencv-dev \
        v4l-utils \
        python3-pip
    
    pip3 install opencv-python-headless \
                 python-socketio \
                 webrtcvad \
                 psutil
}

install_macos_dependencies() {
    # 檢查 Homebrew 是否安裝
    if ! command -v brew &> /dev/null; then
        echo "未檢測到 Homebrew，正在安裝..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    brew install opencv
    brew install v4l-utils
    pip3 install opencv-python-headless \
                 python-socketio \
                 webrtcvad \
                 psutil
}

install_raspberry_dependencies() {
    sudo apt-get update
    sudo apt-get install -y \
        python3-opencv \
        libopencv-dev \
        v4l-utils \
        python3-pip
    
    pip3 install opencv-python-headless \
                 python-socketio \
                 webrtcvad \
                 psutil
}

main() {
    # 檢測作業系統
    case "$(uname -s)" in
        Linux*)
            if [ -f /etc/rpi-issue ]; then
                echo "檢測到 Raspberry Pi"
                install_raspberry_dependencies
            else
                echo "檢測到 Debian/Ubuntu"
                install_debian_dependencies
            fi
            ;;
        Darwin*)
            echo "檢測到 macOS"
            install_macos_dependencies
            ;;
        *)
            echo "不支持的作業系統"
            exit 1
            ;;
    esac
}

main
