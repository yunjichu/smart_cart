import time
from rfid.pn532_uart import PN532UART

class MultiRFIDReader:
    def __init__(self):
        """
        PN532 리더기 3개를 UART 포트를 통해 초기화합니다.
        각 포트는 실제 연결된 라즈베리파이 UART 포트 이름에 맞게 지정해야 합니다.
        """
        self.readers = [
            PN532UART('/dev/ttyAMA0'),   # 기본 UART0
            #PN532UART('/dev/ttyAMA1'),   # 추가 UART1
            #PN532UART('/dev/ttyAMA2'),   # 추가 UART2
        ]

    def read_all(self):
        """
        3개 리더기에서 빠르게 순차적으로 UID를 읽습니다.
        동시에 여러 리더기에 태깅하는 상황은 없다는 전제 하에 빠르게 순회하며 처리합니다.

        Returns:
            dict: {리더기 인덱스: UID} 형식으로 UID 반환 (없으면 빈 딕셔너리)
        """
        result = {}

        for idx, reader in enumerate(self.readers):
            uid = reader.read_uid()
            if uid:
                result[idx] = uid
                print(f"[READER {idx}] UID 인식됨 → {uid}")
            else:
                print(f"[READER {idx}] 카드 없음")

            time.sleep(0.1)  # 너무 빠르게 돌면 충돌할 수 있어 약간의 딜레이

        return result

    def close_all(self):
        """
        모든 시리얼 포트를 안전하게 닫습니다.
        """
        for reader in self.readers:
            reader.close()


# 모듈 단독 실행 시 테스트 동작
if __name__ == "__main__":
    rfid_reader = MultiRFIDReader()

    try:
        while True:
            detected = rfid_reader.read_all()
            if detected:
                print("→ 감지된 카드:", detected)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("종료 중...")
        rfid_reader.close_all()
