"""
Valorant 이미지 수집기
- valorant-api.com (커뮤니티 API, 무료, 인증 불필요)
- 요원 (에이전트) → category: character
- 무기 스킨     → category: skin
- 플레이어카드   → category: illustration
"""

import requests
import logging
from datetime import date

log = logging.getLogger(__name__)

BASE = "https://valorant-api.com/v1"
LANG = "ko-KR"


def fetch_valorant_images(existing_ids: set) -> list:
    """새로운 Valorant 이미지 목록을 반환한다. 이미 존재하는 ID는 건너뜀."""
    today = date.today().isoformat()
    new_images = []

    # ── 요원 (캐릭터) ───────────────────────────
    try:
        r = requests.get(
            f"{BASE}/agents",
            params={"isPlayableCharacter": "true", "language": LANG},
            timeout=30,
        )
        r.raise_for_status()
        agents = r.json().get("data", [])
        log.info(f"Valorant 요원 {len(agents)}명")

        for agent in agents:
            uid = agent["uuid"]
            name = agent.get("displayName", uid)
            thumb = agent.get("displayIconSmall") or agent.get("displayIcon")

            # 캐릭터 (풀포트레이트)
            if agent.get("fullPortrait"):
                img_id = f"val-agent-{uid}-portrait"
                if img_id not in existing_ids:
                    new_images.append({
                        "id": img_id,
                        "game": "valorant",
                        "gameName": "발로란트",
                        "category": "character",
                        "characterName": name,
                        "name": name,
                        "date": today,
                        "thumbnail": thumb,
                        "original": agent["fullPortrait"],
                    })

            # 일러스트 (배경 아트)
            if agent.get("background"):
                img_id = f"val-agent-{uid}-bg"
                if img_id not in existing_ids:
                    new_images.append({
                        "id": img_id,
                        "game": "valorant",
                        "gameName": "발로란트",
                        "category": "illustration",
                        "characterName": name,
                        "name": f"{name} 배경 아트",
                        "date": today,
                        "thumbnail": thumb,
                        "original": agent["background"],
                    })

    except Exception as e:
        log.warning(f"Valorant 요원 수집 실패: {e}")

    # ── 무기 스킨 ────────────────────────────────
    try:
        r = requests.get(f"{BASE}/weapons/skins", params={"language": LANG}, timeout=30)
        r.raise_for_status()
        skins = r.json().get("data", [])
        log.info(f"Valorant 스킨 {len(skins)}개")

        for skin in skins:
            uid = skin["uuid"]
            skin_name = skin.get("displayName", uid)

            # "Standard" (기본 스킨) 및 아이콘 없는 항목 제외
            if "Standard" in skin_name:
                continue
            if not skin.get("displayIcon") and not skin.get("wallpaper"):
                continue

            img_id = f"val-skin-{uid}"
            if img_id in existing_ids:
                continue

            thumb = skin.get("displayIcon")
            original = skin.get("wallpaper") or skin.get("displayIcon")
            if not original:
                continue

            new_images.append({
                "id": img_id,
                "game": "valorant",
                "gameName": "발로란트",
                "category": "skin",
                "characterName": skin_name,
                "name": skin_name,
                "date": today,
                "thumbnail": thumb or original,
                "original": original,
            })

    except Exception as e:
        log.warning(f"Valorant 스킨 수집 실패: {e}")

    # ── 플레이어 카드 (일러스트) ─────────────────
    try:
        r = requests.get(f"{BASE}/playercards", params={"language": LANG}, timeout=30)
        r.raise_for_status()
        cards = r.json().get("data", [])
        log.info(f"Valorant 플레이어카드 {len(cards)}개")

        for card in cards:
            uid = card["uuid"]
            card_name = card.get("displayName", uid)

            if not card.get("largeArt"):
                continue

            img_id = f"val-card-{uid}"
            if img_id in existing_ids:
                continue

            new_images.append({
                "id": img_id,
                "game": "valorant",
                "gameName": "발로란트",
                "category": "illustration",
                "characterName": card_name,
                "name": card_name,
                "date": today,
                "thumbnail": card.get("smallArt") or card.get("largeArt"),
                "original": card["largeArt"],
            })

    except Exception as e:
        log.warning(f"Valorant 플레이어카드 수집 실패: {e}")

    return new_images


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    images = fetch_valorant_images(set())
    print(f"Valorant 총 {len(images)}개 이미지")
    for img in images[:3]:
        print(f"  {img['id']} - {img['name']} [{img['category']}]")
