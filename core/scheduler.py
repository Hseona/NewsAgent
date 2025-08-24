import schedule
import time
from datetime import datetime

def register_schedules(job_func, batch_times):
    for t in batch_times:
        schedule.every().day.at(t).do(job_func)
    
    print("뉴스 모니터링 서비스 시작...")
    print(f"예정된 실행 시간: {', '.join(batch_times)}")
    
    while True:
        # 현재 시간과 다음 실행 예정 시간 정보 출력 (1시간마다)
        now = datetime.now()
        if now.minute == 0:  # 매시 정각에만 상태 출력
            next_run = schedule.next_run()
            if next_run:
                print(f"[{now.strftime('%Y-%m-%d %H:%M')}] 다음 뉴스 수집 예정: {next_run.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"[{now.strftime('%Y-%m-%d %H:%M')}] 스케줄 확인 중...")
        
        schedule.run_pending()
        time.sleep(60)  # 1분(60초) 대기