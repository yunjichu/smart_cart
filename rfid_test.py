from rfid.multi_reader import MultiRFIDReader
import time

reader = MultiRFIDReader()

try:
    while True:
        result = reader.read_all()
        if result:
            print("📥 UID 감지 결과:")
            for idx, uid in result.items():
                print(f" - 리더기 {idx}: {uid}")
        else:
            print("❌ 모든 리더기에서 카드 없음")

        time.sleep(1)

except KeyboardInterrupt:
    print("테스트 종료")
    reader.close_all()
