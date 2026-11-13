"""
Wrapper tương thích ngược cho CatKhungHinh.py
"""
from ai.CatKhungHinh import (
    cat_khung_hinh_tu_video,
    cat_toan_bo_video_trong_thu_muc
)

extract_frames_from_videos = cat_toan_bo_video_trong_thu_muc

if __name__ == "__main__":
    cat_toan_bo_video_trong_thu_muc()
