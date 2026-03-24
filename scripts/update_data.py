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

from fetch_genshin import fetch_genshin_images
from fetch_bluearchive import fetch_bluearchive_images
from fetch_zzz import fetch_zzz_images
from fetch_starrail import fetch_starrail_images

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

    # ── 원신 ─────────────────────────────────────
    log.info("[ 원신 ] 데이터 수집 중...")
    try:
        gi_imgs = fetch_genshin_images(existing_ids)
        new_images.extend(gi_imgs)
        log.info(f"[ 원신 ] 신규 {len(gi_imgs)}개")
    except Exception as e:
        log.error(f"[ 원신 ] 실패: {e}")

    # ── 블루 아카이브 ──────────────────────────────
    log.info("[ 블루 아카이브 ] 데이터 수집 중...")
    try:
        ba_imgs = fetch_bluearchive_images(existing_ids)
        new_images.extend(ba_imgs)
        log.info(f"[ 블루 아카이브 ] 신규 {len(ba_imgs)}개")
    except Exception as e:
        log.error(f"[ 블루 아카이브 ] 실패: {e}")

    # ── 젠레스 존 제로 ─────────────────────────────
    log.info("[ 젠존제 ] 데이터 수집 중...")
    try:
        zzz_imgs = fetch_zzz_images(existing_ids)
        new_images.extend(zzz_imgs)
        log.info(f"[ 젠존제 ] 신규 {len(zzz_imgs)}개")
    except Exception as e:
        log.error(f"[ 젠존제 ] 실패: {e}")

    # ── 붕괴: 스타레일 ─────────────────────────────
    log.info("[ 스타레일 ] 데이터 수집 중...")
    try:
        hsr_imgs = fetch_starrail_images(existing_ids)
        new_images.extend(hsr_imgs)
        log.info(f"[ 스타레일 ] 신규 {len(hsr_imgs)}개")
    except Exception as e:
        log.error(f"[ 스타레일 ] 실패: {e}")

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
