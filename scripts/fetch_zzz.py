"""
젠레스 존 제로 (Zenless Zone Zero) 이미지 수집기
- EnkaNetwork API-docs GitHub 레포 (무료, 인증 불필요)
- 캐릭터 아이콘 → category: character
- 원형 아이콘 → category: illustration
"""

import logging
from datetime import date

import requests

log = logging.getLogger(__name__)

BASE_RAW = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/zzz"
AVATARS_URL = f"{BASE_RAW}/avatars.json"
LOCS_URL = f"{BASE_RAW}/locs.json"
IMG_BASE = "https://enka.network"


def fetch_zzz_images(existing_ids: set) -> list:
    """새로운 젠레스 존 제로 이미지 목록을 반환한다."""
    today = date.today().isoformat()
    new_images = []

    try:
        r_av = requests.get(AVATARS_URL, timeout=30)
        r_av.raise_for_status()
        avatars = r_av.json()

        r_loc = requests.get(LOCS_URL, timeout=30)
        r_loc.raise_for_status()
        locs_en = r_loc.json().get("en", {})

        log.info(f"젠존제 캐릭터 {len(avatars)}명")
    except Exception as e:
        log.warning(f"젠존제 데이터 수집 실패: {e}")
        return new_images

    # 주인공(MC) ID 제외
    MC_IDS = {"2011", "2021"}

    for uid, av in avatars.items():
        if uid in MC_IDS:
            continue

        name_key = av.get("Name", "")
        name = locs_en.get(name_key, name_key)
        rarity = av.get("Rarity", 0)
        image_path = av.get("Image", "")
        circle_path = av.get("CircleIcon", "")

        if not image_path:
            continue

        image_url = IMG_BASE + image_path
        circle_url = IMG_BASE + circle_path if circle_path else image_url

        # 캐릭터 (character)
        img_id = f"zzz-{uid}-icon"
        if img_id not in existing_ids:
            new_images.append({
                "id": img_id,
                "game": "zzz",
                "gameName": "젠레스 존 제로",
                "category": "character",
                "characterName": name,
                "name": name,
                "date": today,
                "thumbnail": circle_url,
                "original": image_url,
            })

        # 원형 아이콘 (illustration)
        if circle_path:
            img_id_circle = f"zzz-{uid}-circle"
            if img_id_circle not in existing_ids:
                new_images.append({
                    "id": img_id_circle,
                    "game": "zzz",
                    "gameName": "젠레스 존 제로",
                    "category": "illustration",
                    "characterName": name,
                    "name": f"{name} 원형 아이콘",
                    "date": today,
                    "thumbnail": circle_url,
                    "original": circle_url,
                })

    return new_images


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    images = fetch_zzz_images(set())
    print(f"젠존제 총 {len(images)}개 이미지")
    for img in images[:3]:
        print(f"  {img['id']} - {img['name']} [{img['category']}]")
