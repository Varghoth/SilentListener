#!/bin/bash

# Удаляем старые файлы блокировки перед запуском VNC сервера
rm -f /tmp/.X*-lock
rm -rf /tmp/.X11-unix/X*

# Удаляем временные файлы PulseAudio
rm -rf /tmp/pulse-* /root/.config/pulse/*

#  Запускаем PulseAudio в фоновом режиме
pulseaudio --start

# Запуск NetworkManager
/usr/sbin/NetworkManager &

# Удаляем конфликтующие процессы панели
killall xfce4-panel || true

# Запуск Proton VPN (если требуется автоподключение)
protonvpn-cli c --fastest &

# Запускаем VNC сервер с желаемым разрешением
export USER=root
tightvncserver :1 -geometry 1280x720 -depth 24

# Применяем тему Arc-Dark
/root/.vnc/apply-theme.sh

# Скрипт завершает работу, так как supervisord будет следить за процессом