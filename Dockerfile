FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    libsqlcipher-dev \
    sqlcipher \
    libgl1 \
    libegl1 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    libx11-xcb1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-shape0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxrender1 \
    libglib2.0-0 \
    libfontconfig1 \
    libsm6 \
    libice6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN chmod +x /app/scripts/start_browser_gui.sh

ENV SPM_DATA_DIR=/app/data
ENV QT_QPA_PLATFORM=xcb

CMD ["/bin/sh", "/app/scripts/start_browser_gui.sh"]
