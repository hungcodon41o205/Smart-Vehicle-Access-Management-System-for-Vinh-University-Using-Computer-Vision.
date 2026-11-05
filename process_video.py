"""
Wrapper tương thích ngược cho XuLyVideo.py
"""
import sys
from XuLyVideo import xu_ly_video_nhan_dien_bien_so

if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else "data/raw_videos/sample_test.mp4"
    xu_ly_video_nhan_dien_bien_so(vid)
