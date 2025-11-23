"""
합성 데이터 생성기
GPT-4 또는 Groq 모델을 사용하여 FreeCAD 명령 학습 데이터를 생성합니다.
"""

import os
import json
from typing import List, Dict
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai 패키지가 설치되지 않았습니다.")


class SyntheticDataGenerator:
    """합성 데이터 생성기"""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        model: str = "openai/gpt-5-mini",
        output_dir: str = "./data/synthetic"
    ):
        """
        합성 데이터 생성기 초기화
        
        Args:
            base_url: LiteLLM proxy URL
            api_key: API 키
            model: 사용할 모델 (openai/gpt-4o 또는 groq/llama-3.3-70b-versatile)
            output_dir: 출력 디렉토리
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 패키지가 필요합니다: uv add openai")
        
        self.base_url = base_url or os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        self.api_key = api_key or os.getenv("LITELLM_API_KEY", "sk-1234")
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenAI 클라이언트 초기화
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def generate_commands(
        self,
        command_type: str = "box",
        count: int = 10,
        language: str = "both"
    ) -> List[str]:
        """
        특정 타입의 명령어를 생성합니다.
        
        Args:
            command_type: 명령 타입 (box, cylinder, sphere, cone, mixed)
            count: 생성할 명령 수
            language: 언어 (korean, english, both)
        
        Returns:
            생성된 명령어 리스트
        """
        prompt = self._create_generation_prompt(command_type, count, language)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 CAD 소프트웨어 사용자입니다. 자연스러운 명령어를 생성해주세요."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        # 응답 파싱
        content = response.choices[0].message.content
        commands = self._parse_commands(content)
        
        return commands
    
    def _create_generation_prompt(
        self,
        command_type: str,
        count: int,
        language: str
    ) -> str:
        """프롬프트 생성"""
        type_descriptions = {
            "box": "박스(box) 생성 명령. 길이, 너비, 높이를 포함해야 함.",
            "cylinder": "실린더(cylinder) 생성 명령. 반지름과 높이를 포함해야 함.",
            "sphere": "구(sphere) 생성 명령. 반지름을 포함해야 함.",
            "cone": "원뿔(cone) 생성 명령. 밑면 반지름, 윗면 반지름, 높이를 포함해야 함.",
            "mixed": "다양한 도형 생성 명령 (박스, 실린더, 구, 원뿔 혼합)"
        }
        
        lang_instruction = {
            "korean": "한국어로만",
            "english": "영어로만",
            "both": "한국어와 영어를 섞어서"
        }
        
        prompt = f"""FreeCAD에서 {type_descriptions[command_type]}

{lang_instruction[language]} {count}개의 자연스러운 명령어를 생성해주세요.

요구사항:
1. 각 명령어는 한 줄로 작성
2. 실제 사용자가 입력할 법한 자연스러운 표현
3. 크기 값은 현실적인 범위 (1~100mm)
4. 다양한 표현 방식 사용 (만들어줘, 생성해, create 등)

형식: 각 명령어를 번호 없이 한 줄씩 작성
"""
        return prompt
    
    def _parse_commands(self, content: str) -> List[str]:
        """생성된 명령어 파싱"""
        lines = content.strip().split('\n')
        commands = []
        
        for line in lines:
            line = line.strip()
            # 번호나 불릿 제거
            if line and not line.startswith('#'):
                # 번호 제거 (1. 또는 1) 형식)
                if line[0].isdigit():
                    line = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                # 불릿 제거
                if line.startswith('-') or line.startswith('*'):
                    line = line[1:].strip()
                
                if line:
                    commands.append(line)
        
        return commands
    
    def generate_dataset(
        self,
        total_count: int = 100,
        save: bool = True
    ) -> List[str]:
        """
        전체 데이터셋 생성
        
        Args:
            total_count: 총 생성할 명령 수
            save: 파일로 저장 여부
        
        Returns:
            생성된 모든 명령어 리스트
        """
        print(f"합성 데이터 생성 시작 (총 {total_count}개)...\n")
        
        all_commands = []
        
        # 각 타입별로 생성
        types = ["box", "cylinder", "sphere", "cone", "mixed"]
        per_type = total_count // len(types)
        
        for cmd_type in types:
            print(f"[{cmd_type}] {per_type}개 생성 중...")
            try:
                commands = self.generate_commands(
                    command_type=cmd_type,
                    count=per_type,
                    language="both"
                )
                all_commands.extend(commands)
                print(f"  ✓ {len(commands)}개 생성 완료")
            except Exception as e:
                print(f"  ✗ 오류: {e}")
        
        print(f"\n총 {len(all_commands)}개 명령어 생성 완료")
        
        # 저장
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"synthetic_commands_{timestamp}.json"
            
            data = {
                "metadata": {
                    "timestamp": timestamp,
                    "model": self.model,
                    "total_count": len(all_commands)
                },
                "commands": all_commands
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"저장 완료: {output_file}")
        
        return all_commands
    
    def _extract_position(self, command: str) -> Dict:
        """
        명령어에서 위치 정보 추출
        
        Args:
            command: 사용자 명령어
        
        Returns:
            위치 정보 딕셔너리
        """
        import re
        position = {}
        
        # 위치 패턴: "at (10, 20, 30)" 또는 "위치 (10, 20, 30)"
        pos_pattern = r'(?:at|위치|position).*?\(?(\d+),?\s*(\d+),?\s*(\d+)\)?'
        match = re.search(pos_pattern, command, re.IGNORECASE)
        if match:
            position = {
                "x": float(match.group(1)),
                "y": float(match.group(2)),
                "z": float(match.group(3))
            }
        
        return position
    
    def _parse_command_to_tool_call(self, command: str) -> Dict:
        """
        명령어를 파싱하여 적절한 tool call로 변환
        
        Args:
            command: 사용자 명령어
        
        Returns:
            tool call 딕셔너리
        """
        import re
        import uuid
        
        # 박스 패턴
        box_patterns = [
            r'(?:박스|box).*?(\d+).*?[xX×*].*?(\d+).*?[xX×*].*?(\d+)',
            r'length.*?(\d+).*?width.*?(\d+).*?height.*?(\d+)',
            r'길이.*?(\d+).*?너비.*?(\d+).*?높이.*?(\d+)',
        ]
        
        for pattern in box_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                # 명령어에서 위치 정보 추출 (선택사항)
                position = self._extract_position(command)
                args = {
                    "length": float(match.group(1)),
                    "width": float(match.group(2)),
                    "height": float(match.group(3)),
                    "name": "Box"
                }
                args.update(position)
                
                return {
                    "id": f"call_{uuid.uuid4().hex[:24]}",
                    "type": "function",
                    "function": {
                        "name": "freecad_create_box",
                        "arguments": json.dumps(args)
                    }
                }
        
        # 실린더 패턴
        cylinder_patterns = [
            r'(?:실린더|cylinder).*?반지름.*?(\d+).*?높이.*?(\d+)',
            r'(?:실린더|cylinder).*?radius.*?(\d+).*?height.*?(\d+)',
        ]
        
        for pattern in cylinder_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                position = self._extract_position(command)
                args = {
                    "radius": float(match.group(1)),
                    "height": float(match.group(2)),
                    "name": "Cylinder"
                }
                args.update(position)
                
                return {
                    "id": f"call_{uuid.uuid4().hex[:24]}",
                    "type": "function",
                    "function": {
                        "name": "freecad_create_cylinder",
                        "arguments": json.dumps(args)
                    }
                }
        
        # 구 패턴
        sphere_patterns = [
            r'(?:구|sphere).*?반지름.*?(\d+)',
            r'(?:구|sphere).*?radius.*?(\d+)',
        ]
        
        for pattern in sphere_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return {
                    "id": f"call_{uuid.uuid4().hex[:24]}",
                    "type": "function",
                    "function": {
                        "name": "freecad_create_sphere",
                        "arguments": json.dumps({
                            "radius": float(match.group(1)),
                            "name": "Sphere"
                        })
                    }
                }
        
        # 원뿔 패턴
        cone_patterns = [
            r'(?:원뿔|cone).*?밑면.*?(\d+).*?윗면.*?(\d+).*?높이.*?(\d+)',
            r'(?:원뿔|cone).*?radius1.*?(\d+).*?radius2.*?(\d+).*?height.*?(\d+)',
        ]
        
        for pattern in cone_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return {
                    "id": f"call_{uuid.uuid4().hex[:24]}",
                    "type": "function",
                    "function": {
                        "name": "freecad_create_cone",
                        "arguments": json.dumps({
                            "radius1": float(match.group(1)),
                            "radius2": float(match.group(2)),
                            "height": float(match.group(3)),
                            "name": "Cone"
                        })
                    }
                }
        
        # 매칭되지 않으면 기본 박스 생성
        return {
            "id": f"call_{uuid.uuid4().hex[:24]}",
            "type": "function",
            "function": {
                "name": "freecad_create_box",
                "arguments": json.dumps({
                    "length": 10.0,
                    "width": 10.0,
                    "height": 10.0,
                    "name": "Box"
                })
            }
        }
    
    def create_training_format(
        self,
        commands: List[str],
        output_file: str = None
    ) -> List[Dict]:
        """
        학습 데이터 포맷으로 변환 (OpenAI function calling 형식)
        
        Args:
            commands: 명령어 리스트
            output_file: 출력 파일 경로
        
        Returns:
            학습 데이터 리스트
        """
        training_data = []
        
        for cmd in commands:
            # 명령어를 파싱하여 tool call 생성
            tool_call = self._parse_command_to_tool_call(cmd)
            
            # OpenAI function calling 포맷
            item = {
                "messages": [
                    {
                        "role": "user",
                        "content": cmd
                    },
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    },
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps({
                            "success": True,
                            "object_name": tool_call["function"]["name"].replace("freecad_create_", "").capitalize(),
                            "message": "객체가 성공적으로 생성되었습니다."
                        })
                    },
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": f"call_{tool_call['id'][5:]}finish",
                            "type": "function",
                            "function": {
                                "name": "finish",
                                "arguments": json.dumps({
                                    "summary": f"{tool_call['function']['name'].replace('freecad_create_', '')} 객체가 성공적으로 생성되었습니다."
                                })
                            }
                        }]
                    }
                ]
            }
            training_data.append(item)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
            print(f"학습 데이터 저장 완료: {output_file}")
        
        return training_data


def main():
    """메인 함수"""
    print("합성 데이터 생성기 시작...\n")
    
    # 생성기 초기화
    generator = SyntheticDataGenerator(
        model="openai/gpt-4o"  # 또는 "groq/llama-3.3-70b-versatile"
    )
    
    # 데이터셋 생성
    commands = generator.generate_dataset(total_count=50)
    
    # 학습 포맷으로 변환
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    training_file = generator.output_dir / f"training_data_{timestamp}.json"
    generator.create_training_format(commands, str(training_file))
    
    print(f"\n{'='*60}")
    print("생성 완료!")
    print(f"  - 명령어 수: {len(commands)}개")
    print(f"  - 저장 위치: {generator.output_dir}")
    print(f"{'='*60}\n")
    
    # 예시 출력
    print("생성된 명령어 예시:")
    for i, cmd in enumerate(commands[:5], 1):
        print(f"  {i}. {cmd}")


if __name__ == "__main__":
    main()

