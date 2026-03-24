"""
붕괴: 스타레일 (Honkai: Star Rail) 이미지 수집기
- Mar-7th/StarRailRes GitHub 레포 (무료, 인증 불필요)
- 캐릭터 아이콘 → category: character
- 캐릭터 프리뷰 → category: illustration
- 캐릭터 풀 포트레이트 → category: skin (배경 포함 전신)
"""

import logging
from datetime import date

import requests

log = logging.getLogger(__name__)

BASE_RAW = "https://raw.githubusercontent.com/Mar-7th/StarRailRes/master"
CHARS_URL = f"{BASE_RAW}/index_new/en/characters.json"


def fetch_starrail_images(existing_ids: set) -> list:
    """새로운 스타레일 이미지 목록을 반환한다."""
    today = date.today().isoformat()
    new_images = []

    try:
        r = requests.get(CHARS_URL, timeout=30)
        r.raise_for_status()
        characters = r.json()
        log.info(f"스타레일 캐릭터 {len(characters)}명")
    except Exception as e:
        log.warning(f"스타레일 캐릭터 목록 수집 실패: {e}")
        return new_images

    for char_id, char in characters.items():
        name = char.get("name", char_id)
        icon_path = char.get("icon", "")
        preview_path = char.get("preview", "")
        portrait_path = char.get("portrait", "")

        if not icon_path:
            continue

        icon_url = f"{BASE_RAW}/{icon_path}"
        preview_url = f"{BASE_RAW}/{preview_path}" if preview_path else icon_url
        portrait_url = f"{BASE_RAW}/{portrait_path}" if portrait_path else preview_url

        # 캐릭터 아이콘 (character)
        img_id = f"hsr-{char_id}-icon"
        if img_id not in existing_ids:
            new_images.append({
                "id": img_id,
                "game": "starrail",
                "gameName": "붕괴: 스타레일",
                "category": "character",
                "characterName": name,
                "name": name,
                "date": today,
                "thumbnail": icon_url,
                "original": icon_url,
            })

        # 프리뷰 이미지 (illustration)
        if preview_path:
            img_id_prev = f"hsr-{char_id}-preview"
            if img_id_prev not in existing_ids:
                new_images.append({
                    "id": img_id_prev,
                    "game": "starrail",
                    "gameName": "붕괴: 스타레일",
                    "category": "illustration",
                    "characterName": name,
                    "name": f"{name} 프리뷰",
                    "date": today,
                    "thumbnail": icon_url,
                    "original": preview_url,
                })

        # 풀 포트레이트 (skin)
        if portrait_path:
            img_id_port = f"hsr-{char_id}-portrait"
            if img_id_port not in existing_ids:
                new_images.append({
                    "id": img_id_port,
                    "game": "starrail",
                    "gameName": "붕괴: 스타레일",
                    "category": "skin",
                    "characterName": name,
                    "name": f"{name} 포트레이트",
                    "date": today,
                    "thumbnail": icon_url,
                    "original": portrait_url,
                })

    return new_images


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    images = fetch_starrail_images(set())
    print(f"스타레일 총 {len(images)}개 이미지")
    for img in images[:3]:
        print(f"  {img['id']} - {img['name']} [{img['category']}]")
