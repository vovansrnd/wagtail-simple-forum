# wagtail-simple-forum

**Wagtail 통합 토론 포럼을 추가합니다. 카테고리, 섹션, 주제, 게시물, 검토, 비공개 메시지, 알림, 검색 및 기존 포럼 앱 가져오기 도구를 제공합니다.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## 주요 기능

- 카테고리 → 섹션 → 주제 → 게시물 계층과 활동 카운터.
- 비공개 메시지 받은 편지함 및 스레드 대화.
- 게스트 스팸 방지, 검토, 검색 및 요청 속도 제한.
- 기존 포럼 가져오기와 리디렉션 도구. 트래픽 전환 전에 dry-run을 검증하세요.

## 요구 사항 및 호환성

- 선언된 종속성: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- Python, Django, Wagtail의 호환성은 함께 확인해야 합니다. 최소 종속성 버전은 모든 버전의 지원을 의미하지 않습니다.

패키지 메타데이터는 Wagtail >= 6.0을 선언하지만 최소 의존성은 모든 버전의 호환성을 입증하지 않습니다. 이 아카이브에는 모든 Django/Wagtail 조합을 다루는 완전한 자동 테스트 매트릭스가 없습니다. 운영 환경을 업그레이드하기 전에 정확한 버전, 데이터베이스, 저장소 백엔드 및 배포 설정을 스테이징에서 검증하세요.

## 설치

Wagtail 프로젝트와 같은 가상 환경에 패키지를 설치하세요:

```bash
pip install wagtail-simple-forum
```

프로젝트의 기존 종속성을 유지하면서 다음 순서로 앱을 추가하세요:

```python
INSTALLED_APPS = [
    # 프로젝트에 필요한 다른 Django/Wagtail 종속성도 유지하세요.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

포럼 URL은 **Wagtail catch-all 경로보다 먼저** 등록하세요. 레거시 리디렉션도 그보다 앞에 있어야 합니다.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # 레거시 경로는 Wagtail catch-all 경로보다 앞에 둡니다.
]
```

`python manage.py migrate wagtail_simple_forum`을 실행하세요.


## 초기 설정

아래는 최소 시작 예제입니다. 모델 이름, API 필드, URL을 실제 구성에 맞추세요.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # 레거시 경로는 Wagtail catch-all 경로보다 앞에 둡니다.
]
```

`python manage.py migrate wagtail_simple_forum`을 실행하세요. 이전 `forum` 앱에서 가져올 때는 먼저 `python manage.py forum_import_from_app --source forum --dry-run`을 실행하세요.

기존 포럼을 가져오기 전에 데이터베이스를 백업하고 `--dry-run`을 실행하세요. 가져오기와 검증이 끝날 때까지 이전 앱을 유지하세요.


## 중요 설정 및 동작

이 디렉터리의 영어 README가 정식 기준 문서이며 전체 설정 표와 자세한 예제를 포함합니다. 이 번역은 실제 설치 절차와 핵심 보안 주의사항을 다룹니다. 고급 설정을 변경하기 전에 영어 문서를 확인하세요.

전체 설정 참조는 [영문 README](README.md)를 확인하세요.

### 중요한 참고 사항

포럼 URL과 레거시 리디렉션은 Wagtail catch-all 경로보다 먼저 배치해야 합니다. 기존 포럼을 가져오기 전에 데이터베이스를 백업하고 먼저 `--dry-run`을 실행하세요.

## 보안 및 운영 지침

- 종속성을 최신 상태로 유지하세요. 사용자 작성 HTML에는 지정된 정리/렌더링 경로를 사용하고, 저장된 댓글이나 포럼 게시물을 무조건 `|safe`로 출력하지 마세요.
- 일반 사용자, 제한 사용자, 중재자, 관리자 계정으로 마이그레이션과 권한을 확인하세요.
- 멀티사이트 환경에서는 설정된 모든 도메인과 알 수 없는 호스트를 테스트하세요. Site를 찾지 못했을 때 조회 범위를 모든 사이트의 레코드로 넓혀서는 안 됩니다.
- API 토큰, SMTP 자격 증명, 비공개 URL은 비밀로 취급하세요. Git에 커밋하거나 공개 버그 보고서에 포함하지 마세요.
- 마이그레이션, 대량 이동, 가져오기 또는 최초 대량 게시 전에 데이터베이스와 미디어 파일을 백업하고 먼저 스테이징에서 실행하세요.

## 권장 조합

- `wagtail-mptt-comments`는 글 댓글을 보완합니다. Prose 이미지 선택기는 사용자 정의 필드가 필요로 할 때만 사용하세요.
- 이미지 디렉터리는 포럼 데이터와 독립적입니다.

## 검증 체크리스트

- [ ] 스테이징에 후보 버전을 설치하고 Python, Django, Wagtail 및 DB 버전을 기록하세요.
- [ ] `python manage.py check`와 패키지 마이그레이션을 실행하세요.
- [ ] 일반 사용자와 제한 사용자로 주요 흐름을 테스트하세요.
- [ ] 로그, 접근 제어, 캐시, 백업 및 복원 절차를 점검하세요.

이 아카이브는 정적 구문 및 패키징 검사를 통과했지만 현재 환경에서 Django/Wagtail 런타임 통합 테스트 전체를 실행하지는 못했습니다. 아래 목록은 모든 조합을 테스트했다는 주장이 아니라 출시 전 필수 확인 항목입니다.

## 문제 해결

흐름이 작동하지 않으면 앱 설정, 마이그레이션, URL 순서, 사용자 권한 및 Django 로그를 확인하세요. 패키지 버전과 예제를 영문 README와 비교하세요.

## 라이선스 및 지원

MIT. 소스 코드: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

