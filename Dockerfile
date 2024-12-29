# Используем легковесный образ Ubuntu
FROM ubuntu:latest

# Обновляем систему и устанавливаем необходимые пакеты
RUN apt-get update && \
    apt-get install -y xfce4 xfce4-goodies tightvncserver dbus-x11 wget curl libavcodec-extra \
    ffmpeg gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav pulseaudio ubuntu-restricted-extras && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

############################# Установка Firefox #############################
RUN wget -O firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" && \
    tar xjf firefox.tar.bz2 -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/local/bin/firefox && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm firefox.tar.bz2

# Устанавливаем Firefox как браузер по умолчанию
RUN update-alternatives --install /usr/bin/x-www-browser x-www-browser /usr/bin/firefox 100 && \
    update-alternatives --set x-www-browser /usr/bin/firefox && \
    update-alternatives --install /usr/bin/gnome-www-browser gnome-www-browser /usr/bin/firefox 100 && \
    update-alternatives --set gnome-www-browser /usr/bin/firefox

########################## ОБОИ ########################################################

# Копируем изображение обоев в контейнер
COPY ./docs/MOUSE.jpg /usr/share/backgrounds/xfce/MOUSE.jpg

# Устанавливаем MOUSE.jpg как обои рабочего стола
RUN mkdir -p /root/.config/xfce4/xfconf/xfce-perchannel-xml/ && \
    echo '<?xml version="1.0" encoding="UTF-8"?>' > /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '<channel name="xfce4-desktop" version="1.0">' >> /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '  <property name="backdrop" type="empty">' >> /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '    <property name="screen0" type="empty">' >> /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '      <property name="monitor0" type="empty">' >> /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '        <property name="workspace0" type="empty">' >> /root/.config/xfce4/xfconf/xfce4-desktop.xml && \
    echo '          <property name="last-image" type="string" value="/usr/share/backgrounds/xfce/MOUSE.jpg"/>' >> /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '        </property>' >> /root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml && \
    echo '      </property>' >> /root/.config/xfce4/xfconf/xfce4-desktop.xml && \
    echo '    </property>' >> /root/.config/xfce4/xfconf/xfce4-desktop.xml && \
    echo '  </property>' >> /root/.config/xfce4/xfconf/xfce4-desktop.xml && \
    echo '</channel>' >> /root/.config/xfce4/xfconf/xfce4-desktop.xml

# Настраиваем VNC-сервер и создаем конфигурацию
RUN mkdir -p /root/.vnc && \
    echo "1234" | vncpasswd -f > /root/.vnc/passwd && \
    chmod 600 /root/.vnc/passwd

# Создаем xstartup файл для запуска Xfce сессии
RUN echo "#!/bin/sh\nxrdb $HOME/.Xresources\nstartxfce4 &" > /root/.vnc/xstartup && \
    chmod +x /root/.vnc/xstartup

# Копируем скрипт запуска
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Устанавливаем команду запуска по умолчанию
CMD ["/usr/local/bin/start.sh"]