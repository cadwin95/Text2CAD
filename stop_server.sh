#!/bin/bash
# FreeCAD Web Viewer 서버 종료 스크립트

echo "🛑 FreeCAD Web Viewer 서버를 종료하는 중..."

# 5000번 포트 사용 프로세스 종료
if lsof -i :5000 > /dev/null 2>&1; then
    lsof -ti :5000 | xargs kill -9 2>/dev/null
    echo "✅ 서버가 종료되었습니다."
else
    echo "ℹ️  실행 중인 서버가 없습니다."
fi

# Flask 앱 프로세스도 확인
APP_PIDS=$(ps aux | grep "web_viewer/app.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$APP_PIDS" ]; then
    echo "🧹 Flask 프로세스 정리 중..."
    echo "$APP_PIDS" | xargs kill -9 2>/dev/null
    echo "✅ Flask 프로세스 종료 완료"
fi

echo ""
echo "🎉 모든 서버 프로세스가 종료되었습니다."


