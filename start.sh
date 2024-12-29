#!/bin/bash

# Удаляем старые файлы блокировки перед запуском VNC сервера
rm -f /tmp/.X*-lock
rm -rf /tmp/.X11-unix/X*

# Запускаем PulseAudio
pulseaudio --start

# Запуск NetworkManager
/usr/sbin/NetworkManager &

# Запуск Proton VPN (если требуется автоподключение)
protonvpn-cli c --fastest &

# Запускаем VNC сервер с желаемым разрешением
export USER=root
tightvncserver :1 -geometry 1280x720 -depth 24

# Запускаем оконный менеджер
xfce4-session &

# Оставляем контейнер в рабочем состоянии
tail -f /dev/null