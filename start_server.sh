#!/bin/bash
# FreeCAD Web Viewer 서버 시작 스크립트

cd "$(dirname "$0")"

# 기존 서버 확인 및 종료
if lsof -i :5000 > /dev/null 2>&1; then
    echo "🛑 기존 서버를 종료하는 중..."
    lsof -ti :5000 | xargs kill -9 2>/dev/null
    sleep 1
fi

echo "🚀 FreeCAD Web Viewer 시작 중..."
echo ""

# 서버 시작 (포그라운드)
uv run python web_viewer/app.py

# Ctrl+C로 종료하면 정리
echo ""
echo "✅ 서버가 종료되었습니다."


