#!/bin/bash

echo "======================================================================"
echo "🌐 FreeCAD Web Viewer 시작"
echo "======================================================================"
echo ""

cd "$(dirname "$0")"

# venv 활성화 (uv 환경)
if [ -d ".venv" ]; then
    echo "✅ venv 활성화 중..."
    source .venv/bin/activate
fi

echo "📡 서버: http://localhost:5000"
echo "🧠 모델: groq/openai/gpt-oss-20b"
echo ""
echo "💡 브라우저를 열고 http://localhost:5000 으로 접속하세요"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

# 서버 시작
cd web_viewer
python3 app.py


