# Используем легковесный образ Debian
FROM debian:bullseye-slim

# Обновляем систему и устанавливаем только необходимые пакеты
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    xfce4 \
    tightvncserver \
    dbus-x11 \
    wget \
    curl \
    libavcodec-extra \
    ffmpeg \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    xfonts-base \
    xfonts-75dpi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем procps для удобства мониторинга
RUN apt-get update && \
    apt-get install -y --no-install-recommends procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Настраиваем VNC-сервер и создаем конфигурацию
RUN mkdir -p /root/.vnc && \
    echo "1234" | vncpasswd -f > /root/.vnc/passwd && \
    chmod 600 /root/.vnc/passwd

# Создаем xstartup файл для запуска Xfce
RUN echo "#!/bin/sh\nxrdb $HOME/.Xresources\nstartxfce4 &" > /root/.vnc/xstartup && \
    chmod +x /root/.vnc/xstartup

# Копируем скрипт запуска
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Устанавливаем команду запуска
CMD ["/usr/local/bin/start.sh"]
