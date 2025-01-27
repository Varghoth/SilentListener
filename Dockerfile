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
    xfonts-75dpi \
    ca-certificates \
    bzip2 \
    python3-tk \
    python3-dev \
    build-essential \
    libsm6 \
    libxext6 \
    libxrender-dev \
    gnome-screenshot \
    x11-xkb-utils \
    xserver-xorg-core \
    mousepad \
    tesseract-ocr \
    supervisor \
    nano \
    xdotool \
    arc-theme && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

    # Установка Python и pip
    RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

    # Установка Python-зависимостей через pip
    RUN pip3 install --no-cache-dir \
        pyautogui \
        pillow \
        qasync \
        pytesseract \
        playwright \
        opencv-python-headless

    # Установка PyQt5 через apt и pip
    RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-pyqt5 \
        python3-pyqt5.qtquick && \
        pip3 install --no-cache-dir PyQt5 PyQt5-sip && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

    # Установка PulseAudio
    RUN apt-get update && apt-get install -y --no-install-recommends pulseaudio && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

    # Настройка PulseAudio
    RUN mkdir -p /root/.config/pulse/ && \
        echo "autospawn = yes" > /root/.config/pulse/client.conf && \
        echo "exit-idle-time = -1" > /root/.config/pulse/daemon.conf

############################# [START] Установка DCA #############################
# Копируем директорию DCA в контейнер
COPY DCA /app/DCA
WORKDIR /app/DCA
############################# [END] Установка DCA #############################

# Сжатие памяти
RUN apt-get update && \
    apt-get install -y --no-install-recommends zram-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo 'zram_enabled=1' >> /etc/default/zram-config

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

############################# [START] SUPERVISORD #############################

# Устанавливаем supervisord
RUN apt-get update && apt-get install -y --no-install-recommends supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем конфигурацию supervisord
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Настраиваем директорию для supervisord
RUN mkdir -p /var/log/supervisor

############################# [-END-] SUPERVISORD #############################

# Копируем скрипт запуска
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Глобальные переменные
ENV DISPLAY=:1

# Установка темы Arc-Dark
RUN echo '#!/bin/sh\n\
sleep 2\n\
xfconf-query -c xsettings -p /Net/ThemeName -s "Arc-Dark"\n\
xfconf-query -c xsettings -p /Net/IconThemeName -s "elementary"' > /root/.vnc/apply-theme.sh && \
    chmod +x /root/.vnc/apply-theme.sh

# Устанавливаем команду запуска
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]