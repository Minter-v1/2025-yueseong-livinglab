# 2025 유성구청 리빙랩 – 이미지 인식 자동화

행복e음 업무 효율화를 위해 개발한 이미지 인식 기반 RPA 프로젝트입니다.  
GUI 화면을 캡처하고 **템플릿 매칭 + 색상/직선 분석**으로 버튼과 입력 필드를 찾은 뒤 `pyautogui`로 실제 시스템을 조작합니다.  

이 문서는 발표와 유지보수를 대비해 **이미지 처리 파이프라인, 핵심 모듈, 템플릿 관리 방법**을 중심으로 정리했습니다.

---

## 전체 파이프라인 개요

1. **화면 확보 (`ScreenCapture`)**  
   - 전체 화면 또는 특정 윈도우를 PNG로 저장.  
   - macOS에서는 AppleScript로 타깃 창만 캡처 가능.  
   - Retina/배율 환경에서 원본 해상도를 그대로 유지합니다.

2. **팝업 경계 감지 (`DialogDetector`)**  
   - Otsu 이진화 → 모폴로지 → 컨투어 분석으로 가장 큰 팝업을 식별.  
   - ROI(관심 영역)를 산출해 템플릿 매칭 범위를 제한.  
   - 선형(Hough) 기반 대안 알고리즘 제공.

3. **UI 요소 매칭 (`ImageMatcher`)**  
   - 다중 배율 탐색: 템플릿을 0.6~2.0배로 확대/축소하여 매칭.  
   - 다중 모드 비교  
     | 모드 | 설명 |
     |------|------|
     | `gray` | 그레이스케일 |
     | `color` | RGB 전체 |
     | `canny` | 엣지 강조 |
     | `sat` | HSV 포화도 채널 |
   - `TM_CCORR_NORMED`, `TM_CCOEFF_NORMED` 등 여러 OpenCV 매칭 방식 조합.  
   - 템플릿의 알파/엣지 정보를 마스크로 활용해 내부 텍스트 변화에 둔감.  
   - **색상 힌트 + 직선 검증**  
     - 템플릿의 HSV 통계를 추출해 색 마스크 생성, 후보 영역을 필터링.  
     - HoughLinesP로 수평/수직 직선이 충분한지 확인하여 파란색 `조회` 버튼처럼 독특한 색상의 요소 인식률을 높임.

4. **좌표 보정**  
   - 스크린샷 해상도와 실제 모니터 해상도를 비교해 Retina 배율을 보정.  
   - 매칭 결과를 GUI 제어가 사용하는 절대좌표로 변환 후 캐싱.

5. **자동 조작 (`GUIAutomation`, `SearchAutomationService`)**  
   - 입력 필드 포커스 → 기존 값 전체 선택 → 삭제 → 주민번호 타이핑.  
   - 검색/초기화 버튼 클릭, 체크박스 개수 파악 등 반복 동작 수행.  
   - macOS에서 modifier 키가 눌린 채 고정되는 문제를 방지하기 위해 hotkey 이후 강제 `keyUp`을 호출.

---

## 디렉터리 개요

```
2025-ys-livinglab/
├── src/
│   ├── ui/                # Tkinter GUI
│   ├── services/          # 업무 로직 (Excel, 검색 자동화)
│   └── core/              # 이미지/화면 제어 모듈
├── data/
│   ├── templates_mac/     # macOS용 기본 템플릿
│   ├── templates_window/  # Windows용 기본 템플릿
│   └── templates_real/    # 실사용 환경에서 추출한 템플릿
├── tools/                 # 템플릿 생성 유틸리티
└── tests/                 # 템플릿 검증/좌표 확인 스크립트
```

---

## 핵심 모듈 설명

| 모듈 | 설명 | 주요 역할 |
|------|------|-----------|
| `src/ui/main_window.py` | Tkinter 기반 운영자 GUI | 입력/결과 파일 선택, 진행 상황 표시, 자동화 스레드 관리 |
| `src/services/search_service.py` | 자동화 서비스 | 주민등록번호 검색, UI 요소 탐색 및 클릭, 결과 수집 |
| `src/core/screen_capture.py` | 화면 캡처 | 전체/부분 스크린샷, macOS AppleScript 기반 윈도우 캡처 |
| `src/core/dialog_detector.py` | 팝업 경계 검출 | 밝기 이진화 + 컨투어로 팝업 ROI 산출, Hough 기반 대안 지원 |
| `src/core/image_matcher.py` | 템플릿 매칭 엔진 | 다중 배율·다중 모드 매칭, 색상 힌트 + 직선 검증, 마스크 처리 |
| `src/core/automation.py` | GUI 제어 유틸리티 | 마우스/키보드 동작, 안전 지연, 클립보드 붙여넣기 |
| `tools/create_templates.py` | 템플릿 생성 도구 | Mock 시스템에서 인터랙티브로 UI 캡처 |
| `test_detect_coordinates.py` | 검증 스크립트 | 단일 이미지에서 경계 검출 + 템플릿 매칭 결과 시각화 |

---

## 이미지 매칭 세부 전략

### 1. 다중 배율 & 다중 모드
- `ImageMatcher`는 `search_scales` 목록에 따라 템플릿을 확대/축소하며 탐색합니다.
- 각 배율에 대해 `gray`, `color`, `canny`, `sat` 모드를 순회하면서 신뢰도가 가장 높은 조합을 선택합니다.
- 로그에 `method / mode / scale`이 출력되어 현장 튜닝이 쉽습니다.

### 2. 마스크 기반 정밀도 향상
- 템플릿의 알파 채널 또는 엣지(Canny)를 마스크로 사용하여 버튼 테두리·아이콘 중심으로 비교합니다.
- 내부 텍스트(예: 커서, 플레이스홀더) 변화에 덜 민감합니다.

### 3. 색상 힌트 + 직선 검증
- 템플릿의 HSV 평균·표준편차를 기반으로 색 범위를 계산하고, `cv2.inRange`로 후보 영역을 찾습니다.
- 모폴로지 연산으로 노이즈를 제거하고, 색상 커버리지·가로/세로 비율을 점수화합니다.
- HoughLinesP로 수평/수직 직선이 존재하는지 검증하여 실제 버튼 형태인지 확인합니다.
- 최종 점수를 0.65~0.98 신뢰도로 환산하여 기존 템플릿 매칭보다 높을 경우 교체합니다.

### 4. Retina/배율 대응
- 스크린샷 해상도와 `pyautogui.size()`를 비교해 배율을 계산합니다.
- 좌표/크기를 1배 스케일 기준으로 재환산하여 마우스 클릭이 정확히 맞도록 보정합니다.

---

## 템플릿 관리 & 교체 가이드

1. **환경별 폴더**  
   - `templates_mac`, `templates_window`, `templates_real` 디렉터리를 운영.  
   - `SearchAutomationService`가 OS를 감지해 올바른 디렉터리를 선택합니다.

2. **자동 생성 도구 사용**
   ```bash
   ./venv/bin/python tools/create_templates.py
   ```
   - Mock 시스템을 띄우고 안내에 따라 마우스를 요소 중앙에 위치시키면 캡처합니다.
   - 캡처 시 가능한 한 **테두리를 포함한 넉넉한 영역**을 잡아주는 것이 안정적입니다.

3. **수동 조정 팁**
   - 텍스트나 강조선이 바뀌면 템플릿을 다시 캡처하세요.  
   - Retina 환경에서 캡처한 템플릿은 2배 크기일 수 있으므로 환경별 폴더를 분리합니다.

4. **템플릿 검증**
   ```bash
   pip install -r requirements.txt
   python test_detect_coordinates.py data/templates/img_org.jpeg
   ```
   - 출력 로그에서 각 템플릿의 신뢰도와 `mode/scale`을 확인합니다.
   - `result_coordinates.png`를 열어 실제 위치를 시각적으로 검토합니다.

---

## 자동화 실행 전 체크리스트

- macOS에서는 **손쉬운 사용 + 입력 모니터링** 권한을 `python`, 터미널 앱에 부여해야 `pyautogui` 입력이 동작합니다.
- 행복e음(또는 Mock) 창이 화면에 떠 있고 다른 창에 가려지지 않았는지 확인합니다.
- 실행 중에는 마우스/키보드를 수동으로 조작하지 않아야 좌표가 어긋나지 않습니다.
- 에러 발생 시 `행복e음 자동화 프로그램` GUI 로그 또는 `test_detect_coordinates.py`를 활용해 원인을 추적합니다.

---

## 빌드 & 실행

```bash
python3 -m venv venv
source venv/bin/activate            # Windows는 venv\Scripts\activate
pip install -r requirements.txt
python -m src.ui.main_window
```

엑셀 입력 파일을 지정하고 **시작** 버튼을 누르면 주민등록번호 조회 자동화가 진행됩니다.

---

## 발표 시 강조 포인트

- **이미지 인식 파이프라인**  
  화면 확보 → ROI 추출 → 다중 템플릿 매칭 → 색상/직선 검증 → 좌표 보정 → GUI 제어.
- **레거시 시스템 대응 전략**  
  API가 없는 행복e음 환경에서도 화면 인식을 통해 RPA를 구성.
- **신뢰도 향상 기법**  
  - 멀티스케일/멀티모드 템플릿 매칭  
  - 엣지/알파 마스크 활용  
  - HSV 색상 힌트 + Hough 직선 검증  
  - Retina 스케일 보정 및 modifier 키 해제
- **유지보수 용이성**  
  템플릿 생성 도구, 좌표 검증 스크립트, OS별 템플릿 분리, 풍부한 로그 출력으로 현장 대응이 쉽습니다.

이 문서를 기반으로 시스템 구조와 이미지 처리 기법을 설명하면, 프로젝트의 기술적 강점을 명확히 전달할 수 있습니다.
