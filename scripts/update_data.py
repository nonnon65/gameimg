"""
메인 데이터 갱신 스크립트
- 기존 data/images.json 을 읽어 새 이미지만 추가
- 게임별 fetch_*.py 를 순서대로 실행
- 결과를 date 내림차순으로 정렬 후 저장

사용법:
  python scripts/update_data.py

GitHub Actions 에서 매일 자동 실행됨 (.github/workflows/update-data.yml)
"""

import json
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

# 스크립트 디렉터리를 sys.path 에 추가
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from fetch_lol import fetch_lol_images
from fetch_valorant import fetch_valorant_images

DATA_DIR = SCRIPTS_DIR.parent / "data"
IMAGES_FILE = DATA_DIR / "images.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def load_existing() -> dict:
    if IMAGES_FILE.exists():
        with open(IMAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lastUpdated": "", "images": []}


def save(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(IMAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"저장 완료: {IMAGES_FILE}")


def main():
    log.info("=== GameGallery 데이터 갱신 시작 ===")

    existing = load_existing()
    existing_ids: set = {img["id"] for img in existing.get("images", [])}
    log.info(f"기존 이미지: {len(existing_ids)}개")

    new_images = []

    # ── LoL ─────────────────────────────────────
    log.info("[ LoL ] 데이터 수집 중...")
    try:
        lol_imgs = fetch_lol_images(existing_ids)
        new_images.extend(lol_imgs)
        log.info(f"[ LoL ] 신규 {len(lol_imgs)}개")
    except Exception as e:
        log.error(f"[ LoL ] 실패: {e}")

    # ── Valorant ─────────────────────────────────
    log.info("[ Valorant ] 데이터 수집 중...")
    try:
        val_imgs = fetch_valorant_images(existing_ids)
        new_images.extend(val_imgs)
        log.info(f"[ Valorant ] 신규 {len(val_imgs)}개")
    except Exception as e:
        log.error(f"[ Valorant ] 실패: {e}")

    # ── 병합 & 정렬 ──────────────────────────────
    all_images = existing.get("images", []) + new_images

    # date 내림차순, 같은 날짜면 id 순
    all_images.sort(key=lambda x: (x.get("date", ""), x.get("id", "")), reverse=True)

    updated_data = {
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_note": "이 파일은 scripts/update_data.py 가 자동으로 갱신합니다. 직접 수정하지 마세요.",
        "images": all_images,
    }

    save(updated_data)

    log.info(f"=== 완료: 전체 {len(all_images)}개 (신규 {len(new_images)}개) ===")
    return len(new_images)


if __name__ == "__main__":
    added = main()
    sys.exit(0 if added >= 0 else 1)
