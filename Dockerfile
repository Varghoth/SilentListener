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

############################# [START] Установка Firefox #############################
# Используем --no-check-certificate для обхода ошибки сертификатов
RUN wget --no-check-certificate -O firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" && \
    tar xjf firefox.tar.bz2 -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/local/bin/firefox && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm firefox.tar.bz2

# Устанавливаем Firefox как браузер по умолчанию
RUN update-alternatives --install /usr/bin/x-www-browser x-www-browser /usr/bin/firefox 100 && \
    update-alternatives --set x-www-browser /usr/bin/firefox && \
    update-alternatives --install /usr/bin/gnome-www-browser gnome-www-browser /usr/bin/firefox 100 && \
    update-alternatives --set gnome-www-browser /usr/bin/firefox

# Настройка Firefox
RUN mkdir -p /root/.mozilla/firefox/default-release && \
    echo 'user_pref("browser.sessionstore.resume_from_crash", false);' >> /root/.mozilla/firefox/default-release/prefs.js && \
    echo 'user_pref("browser.tabs.warnOnClose", false);' >> /root/.mozilla/firefox/default-release/prefs.js && \
    echo 'user_pref("media.hardware-video-decoding.enabled", false);' >> /root/.mozilla/firefox/default-release/prefs.js && \
    echo 'user_pref("gfx.webrender.enabled", false);' >> /root/.mozilla/firefox/default-release/prefs.js \
    echo 'user_pref("media.peerconnection.enabled", false);' >> /root/.mozilla/firefox/default-release/prefs.js

############################# [END] Установка Firefox #############################

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

# Вносим в конт настроенный профиль firefox
COPY fox.blocked.settings/autoconfig.js /opt/firefox/defaults/pref/autoconfig.js
COPY fox.blocked.settings/firefox.cfg /opt/firefox/firefox.cfg

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