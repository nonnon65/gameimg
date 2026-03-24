"""
원신 (Genshin Impact) 이미지 수집기
- genshin-optimizer GitHub 레포 (무료, 인증 불필요)
- 캐릭터 아이콘 → category: character
- 캐릭터 사이드 아이콘 → category: illustration
"""

import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import requests

log = logging.getLogger(__name__)

BASE_RAW = "https://raw.githubusercontent.com/frzyc/genshin-optimizer/master/libs/gi/assets/src/gen/chars"
INDEX_URL = f"{BASE_RAW}/index.ts"


def _camel_to_name(s: str) -> str:
    """CamelCase 폴더명을 공백 구분 이름으로 변환 (예: HuTao → Hu Tao)."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", s)


def _fetch_char_icons(char: str) -> tuple[str, dict | None]:
    url = f"{BASE_RAW}/{char}/index.ts"
    try:
        r = requests.get(url, timeout=20)
        if not r.ok:
            return char, None
        icon_m = re.search(r"import icon from './(.+?)'", r.text)
        side_m = re.search(r"import iconSide from './(.+?)'", r.text)
        return char, {
            "icon": icon_m.group(1) if icon_m else None,
            "iconSide": side_m.group(1) if side_m else None,
        }
    except Exception as e:
        log.warning(f"Genshin char {char} fetch 실패: {e}")
        return char, None


def fetch_genshin_images(existing_ids: set) -> list:
    """새로운 원신 이미지 목록을 반환한다."""
    today = date.today().isoformat()
    new_images = []

    # ── 캐릭터 폴더 목록 ─────────────────────────
    try:
        r = requests.get(INDEX_URL, timeout=30)
        r.raise_for_status()
        char_names = re.findall(r"import (\w+) from './\w+'", r.text)
        log.info(f"원신 캐릭터 {len(char_names)}명")
    except Exception as e:
        log.warning(f"원신 캐릭터 목록 수집 실패: {e}")
        return new_images

    # ── 개별 아이콘 파일명 병렬 수집 ─────────────
    char_data: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(_fetch_char_icons, c): c for c in char_names}
        for f in as_completed(futures):
            char, data = f.result()
            if data:
                char_data[char] = data

    log.info(f"원신 아이콘 데이터 수집 완료: {len(char_data)}명")

    # ── 이미지 엔트리 생성 ────────────────────────
    for char, data in char_data.items():
        display_name = _camel_to_name(char)
        char_base = f"{BASE_RAW}/{char}"

        # 캐릭터 아이콘 (character)
        if data.get("icon"):
            img_id = f"gi-{char.lower()}-icon"
            if img_id not in existing_ids:
                new_images.append({
                    "id": img_id,
                    "game": "genshin",
                    "gameName": "원신",
                    "category": "character",
                    "characterName": display_name,
                    "name": display_name,
                    "date": today,
                    "thumbnail": f"{char_base}/{data['icon']}",
                    "original": f"{char_base}/{data['icon']}",
                })

        # 사이드 아이콘 (illustration)
        if data.get("iconSide"):
            img_id = f"gi-{char.lower()}-side"
            if img_id not in existing_ids:
                new_images.append({
                    "id": img_id,
                    "game": "genshin",
                    "gameName": "원신",
                    "category": "illustration",
                    "characterName": display_name,
                    "name": f"{display_name} 사이드",
                    "date": today,
                    "thumbnail": f"{char_base}/{data['icon']}",
                    "original": f"{char_base}/{data['iconSide']}",
                })

    return new_images


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    images = fetch_genshin_images(set())
    print(f"원신 총 {len(images)}개 이미지")
    for img in images[:3]:
        print(f"  {img['id']} - {img['name']} [{img['category']}]")
