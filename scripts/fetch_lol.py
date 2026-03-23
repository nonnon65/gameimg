"""
League of Legends 이미지 수집기
- Riot Data Dragon API (무료, 인증 불필요)
- 챔피언 기본 스킨 → category: character
- 챔피언 대체 스킨 → category: skin
"""

import requests
import time
import logging
from datetime import date

log = logging.getLogger(__name__)

BASE = "https://ddragon.leagueoflegends.com"
LANG = "ko_KR"


def get_latest_version() -> str:
    r = requests.get(f"{BASE}/api/versions.json", timeout=30)
    r.raise_for_status()
    return r.json()[0]


def get_champions(version: str) -> dict:
    url = f"{BASE}/cdn/{version}/data/{LANG}/champion.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()["data"]


def get_champion_detail(version: str, champ_id: str) -> dict:
    url = f"{BASE}/cdn/{version}/data/{LANG}/champion/{champ_id}.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()["data"]
    return data[champ_id]


def fetch_lol_images(existing_ids: set) -> list:
    """새로운 LoL 이미지 목록을 반환한다. 이미 존재하는 ID는 건너뜀."""
    version = get_latest_version()
    log.info(f"LoL version: {version}")

    champions = get_champions(version)
    today = date.today().isoformat()
    new_images = []

    for idx, (champ_key, _) in enumerate(champions.items()):
        try:
            detail = get_champion_detail(version, champ_key)
            champ_name = detail["name"]

            for skin in detail["skins"]:
                num = skin["num"]
                img_id = f"lol-{champ_key}-skin-{num}"

                if img_id in existing_ids:
                    continue

                category = "character" if num == 0 else "skin"
                skin_name = champ_name if num == 0 else skin["name"]

                new_images.append({
                    "id": img_id,
                    "game": "lol",
                    "gameName": "리그 오브 레전드",
                    "category": category,
                    "characterName": champ_name,
                    "name": skin_name,
                    "date": today,
                    "thumbnail": f"{BASE}/cdn/img/champion/loading/{champ_key}_{num}.jpg",
                    "original": f"{BASE}/cdn/img/champion/splash/{champ_key}_{num}.jpg",
                })

            # 요청 간격 (Rate limit 방지)
            if idx % 10 == 9:
                time.sleep(0.5)

        except Exception as e:
            log.warning(f"  Champion {champ_key} 처리 실패: {e}")
            continue

    return new_images


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    images = fetch_lol_images(set())
    print(f"LoL 총 {len(images)}개 이미지")
    for img in images[:3]:
        print(f"  {img['id']} - {img['name']}")
