# 모델 선택 전략 (Model Selection Strategy)

현재 프로젝트의 각 단계별로 최적의 모델을 선택하는 전략을 정리합니다.

## 현재 상황

### 문제점
- **코드 생성 단계**와 **VLM 검증 단계**가 동일한 모델(`gpt-4o`)을 사용
- 각 단계의 특성에 맞는 모델 선택이 되지 않음
- 비용 최적화 여지가 있음

### 사용 가능한 모델
- `gpt-4`: OpenAI GPT-4 (고성능, 비용 높음)
- `gpt-4o`: OpenAI GPT-4o (고성능, Vision 지원, 비용 중간)
- `groq-llama3`: Groq Llama3-70B (빠름, 비용 낮음, Vision 미지원)
- `llava`: LLaVA Vision 모델 (로컬, Vision 전용, 비용 매우 낮음)

## 단계별 모델 선택 전략

### 1. 코드 생성 단계 (OCXCodeAgent)

**특성:**
- 구조화된 Python 코드 생성
- OCXBuilder SDK API 사용
- 정확성과 일관성이 매우 중요
- 복잡한 추론과 도메인 지식 필요

**권장 모델:**
- **1순위**: `gpt-4o` (현재 사용 중)
  - 이유: 코드 생성 품질이 우수하고, Vision 지원으로 향후 확장 가능
  - 비용: 중간
  - 속도: 빠름

- **2순위**: `gpt-4`
  - 이유: 더 높은 정확성 필요 시
  - 비용: 높음
  - 속도: 느림

- **3순위**: `groq-llama3` (실험적)
  - 이유: 비용 절감이 중요하고, 간단한 케이스만 처리할 때
  - 비용: 매우 낮음
  - 속도: 매우 빠름
  - 주의: 복잡한 케이스에서 품질 저하 가능

**결론**: `gpt-4o` 유지 권장

---

### 2. VLM 검증 단계 (VLMValidator)

**특성:**
- 생성된 3D 모델 이미지(PNG) 분석
- 사용자 요청과 결과 매칭 검증
- 비교적 단순한 작업 (이미지 → JSON 응답)
- Vision 능력이 핵심

**권장 모델:**
- **1순위**: `gpt-4o` (현재 사용 중)
  - 이유: Vision 품질 우수, JSON 구조화 응답 정확
  - 비용: 중간
  - 속도: 빠름

- **2순위**: `llava` (로컬 모델)
  - 이유: 비용 절감이 중요할 때, 로컬 실행 가능
  - 비용: 매우 낮음 (로컬 실행)
  - 속도: 중간 (로컬 하드웨어에 따라 다름)
  - 주의: JSON 파싱 품질이 GPT-4o보다 낮을 수 있음

- **3순위**: `gpt-4` (비권장)
  - 이유: Vision 지원하지만 비용 대비 효율 낮음

**결론**: 
- **프로덕션**: `gpt-4o` 유지
- **비용 절감 필요 시**: `llava` 고려 (로컬 서버 설정 필요)

---

## 권장 구성

### 구성 1: 품질 우선 (현재 구성)
```yaml
코드 생성: gpt-4o
VLM 검증: gpt-4o
```
- **장점**: 최고 품질, 일관성
- **단점**: 비용이 높음
- **적용 시나리오**: 프로덕션, 정확성이 중요한 경우

### 구성 2: 비용 최적화
```yaml
코드 생성: gpt-4o
VLM 검증: llava (로컬)
```
- **장점**: 검증 단계 비용 절감
- **단점**: LLaVA 서버 설정 필요, 검증 품질 약간 저하 가능
- **적용 시나리오**: 개발/테스트, 대량 처리

### 구성 3: 극단적 비용 절감 (실험적)
```yaml
코드 생성: groq-llama3
VLM 검증: llava (로컬)
```
- **장점**: 최소 비용
- **단점**: 품질 저하 가능성 높음
- **적용 시나리오**: 프로토타입, 간단한 케이스만

---

## 구현 방안

### 옵션 1: 환경 변수로 분리 (권장)
```bash
# .env
CODE_GENERATION_MODEL=gpt-4o
VLM_VALIDATION_MODEL=gpt-4o
# 또는
VLM_VALIDATION_MODEL=llava  # 비용 절감 시
```

### 옵션 2: API 요청에서 지정
```json
{
  "message": "deck 생성",
  "model": "gpt-4o",  // 코드 생성용
  "vlm_model": "llava"  // VLM 검증용 (선택)
}
```

### 옵션 3: 설정 파일 분리
`model_config.yaml` 파일로 관리

---

## 성능 비교 예상

| 구성 | 코드 생성 품질 | VLM 검증 품질 | 비용/요청 | 속도 |
|------|---------------|--------------|----------|------|
| gpt-4o + gpt-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 높음 | 빠름 |
| gpt-4o + llava | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 중간 | 중간 |
| groq-llama3 + llava | ⭐⭐⭐ | ⭐⭐⭐ | 매우 낮음 | 빠름 |

---

## 구현 완료 사항

1. ✅ 모델 선택 전략 문서화 (이 문서)
2. ✅ 환경 변수로 모델 분리 가능하도록 코드 수정
3. ✅ API 요청에서 VLM 모델 별도 지정 가능

## 사용 방법

### 방법 1: 환경 변수로 설정 (권장)

`.env` 파일에 추가:
```bash
# 코드 생성 모델 (기본값: gpt-4o)
CODE_GENERATION_MODEL=gpt-4o

# VLM 검증 모델 (기본값: gpt-4o)
VLM_VALIDATION_MODEL=gpt-4o
# 또는 비용 절감을 위해
VLM_VALIDATION_MODEL=llava
```

### 방법 2: API 요청에서 지정

```json
{
  "message": "20m x 10m deck 생성",
  "model": "gpt-4o",           // 코드 생성용
  "vlm_model": "llava",        // VLM 검증용 (선택)
  "enable_validation": true
}
```

### 방법 3: 코드에서 직접 지정

```python
from src.agent.generative_design import GenerativeDesignCoordinator
from src.agent.vlm_validator import VLMValidator

# 코드 생성 모델 지정
coordinator = GenerativeDesignCoordinator(model="gpt-4o")

# VLM 검증 모델 지정
validator = VLMValidator(model="llava")
```

## 다음 단계

1. ⏳ LLaVA 로컬 서버 설정 가이드 추가
2. ⏳ 성능 벤치마크 테스트
3. ⏳ 모델별 품질 비교 실험

