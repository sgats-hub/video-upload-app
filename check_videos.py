from app import app, db, Video
from datetime import datetime
from collections import Counter

with app.app_context():
    videos = Video.query.all()
    print(f'Total videos: {len(videos)}')
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_videos = [v for v in videos if v.uploaded_at.strftime('%Y-%m-%d') == today]
    print(f'Today videos ({today}): {len(today_videos)}')
    
    for v in today_videos:
        print(f'ID:{v.id}, filename:{v.filename}, status:{v.status}, uploaded_at:{v.uploaded_at}')
    
    print('\nStatus counts:')
    print(Counter([v.status for v in videos]))
