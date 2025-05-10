from rfid.multi_reader import MultiRFIDReader
import time

reader = MultiRFIDReader()

try:
    while True:
        tags=reader.read_all()
        if tags:
            print("태그 인식됨:")
            for idx, uid in tags.items():
                print(f" 리더기 {idx}: {uid}")
        else:
            print("태그 없음")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("테스트 종료")

