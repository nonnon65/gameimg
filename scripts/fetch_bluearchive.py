"""
블루 아카이브 (Blue Archive) 이미지 수집기
- SchaleDB GitHub 레포 (무료, 인증 불필요)
- 학생 컬렉션 일러스트 → category: character
- 학생 아이콘 → category: illustration
"""

import logging
from datetime import date

import requests

log = logging.getLogger(__name__)

BASE_DATA = "https://raw.githubusercontent.com/SchaleDB/SchaleDB/main"
STUDENTS_URL = f"{BASE_DATA}/data/en/students.min.json"
IMG_COLLECTION = BASE_DATA + "/images/student/collection/{id}.webp"
IMG_ICON = BASE_DATA + "/images/student/icon/{id}.webp"


def fetch_bluearchive_images(existing_ids: set) -> list:
    """새로운 블루 아카이브 이미지 목록을 반환한다."""
    today = date.today().isoformat()
    new_images = []

    try:
        r = requests.get(STUDENTS_URL, timeout=30)
        r.raise_for_status()
        students = r.json()
        log.info(f"블루 아카이브 학생 {len(students)}명")
    except Exception as e:
        log.warning(f"블루 아카이브 학생 목록 수집 실패: {e}")
        return new_images

    for student in students:
        sid = student.get("Id")
        name = student.get("Name", str(sid))
        released = student.get("IsReleased", [True])
        # IsReleased는 [글로벌, JP, ...] 형태 — 하나라도 출시된 캐릭터만 포함
        if not any(released):
            continue

        # 컬렉션 일러스트 (character)
        img_id = f"ba-student-{sid}-collection"
        if img_id not in existing_ids:
            new_images.append({
                "id": img_id,
                "game": "bluearchive",
                "gameName": "블루 아카이브",
                "category": "character",
                "characterName": name,
                "name": name,
                "date": today,
                "thumbnail": IMG_ICON.format(id=sid),
                "original": IMG_COLLECTION.format(id=sid),
            })

        # 아이콘 (illustration)
        img_id_icon = f"ba-student-{sid}-icon"
        if img_id_icon not in existing_ids:
            new_images.append({
                "id": img_id_icon,
                "game": "bluearchive",
                "gameName": "블루 아카이브",
                "category": "illustration",
                "characterName": name,
                "name": f"{name} 아이콘",
                "date": today,
                "thumbnail": IMG_ICON.format(id=sid),
                "original": IMG_ICON.format(id=sid),
            })

    return new_images


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    images = fetch_bluearchive_images(set())
    print(f"블루 아카이브 총 {len(images)}개 이미지")
    for img in images[:3]:
        print(f"  {img['id']} - {img['name']} [{img['category']}]")
