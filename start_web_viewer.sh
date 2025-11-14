#!/bin/bash

echo "======================================================================"
echo "🌐 FreeCAD Web Viewer 시작"
echo "======================================================================"
echo ""
echo "📡 서버: http://localhost:5000"
echo "🧠 모델: groq/openai/gpt-oss-20b"
echo ""
echo "💡 브라우저가 자동으로 열립니다..."
echo ""

# 서버 시작
cd "$(dirname "$0")/web_viewer"
python3 app.py &

# PID 저장
SERVER_PID=$!

# 서버 시작 대기
sleep 3

# 브라우저 열기
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:5000
fi

echo ""
echo "======================================================================"
echo "✅ 서버가 시작되었습니다!"
echo "======================================================================"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

# Ctrl+C 핸들러
trap "echo ''; echo '서버를 종료합니다...'; kill $SERVER_PID; exit 0" INT

# 서버 프로세스 대기
wait $SERVER_PID

