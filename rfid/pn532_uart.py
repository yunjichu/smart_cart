import serial
import time

class PN532UART:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(1.0)
        self.ser.reset_input_buffer()

    def read_uid(self) -> str | None:
        #PN532 리더기로부터 카드 UID를 읽습니다.
        #InListPassiveTarget 명령어를 사용하여 ISO14443A 태그를 검색합니다.
        # PN532 UART 프레임 (InListPassiveTarget: D4 4A 01 00)
        cmd = b'\x00\x00\xFF\x04\xFC\xD4\x4A\x01\x00\xE1\x00'
        # 입력 버퍼 초기화 후 명령 전송
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        time.sleep(0.3)

        if self.ser.in_waiting:
            response = self.ser.read(self.ser.in_waiting)
            print(f"[DEBUG] 응답 raw: {response.hex().upper()}")  # 로그 확인용

        # 응답 안에 D5 4B 응답 패턴이 있는지 확인
            if b'\xD5\x4B' in response:
                try:
                    idx = response.index(b'\xD5\x4B')
                    uid_len = response[idx + 3]  # UID 길이
                    uid_bytes = response[idx + 4 : idx + 4 + uid_len]
                    return uid_bytes.hex().upper()
                except Exception as e:
                    print(f"[ERROR] UID 추출 중 오류: {e}")
        return None



    def _extract_uid(self, data: bytes) -> str | None:
        """
        수신된 바이트 데이터에서 UID를 추출합니다.
        PN532 리더기의 응답 프로토콜에 따라 실제 구현 필요.

        Args:
            data (bytes): PN532로부터 받은 원시 바이트 응답

        Returns:
            UID 문자열 또는 파싱 실패 시 None
        """
        if len(data) >= 6:
            # 실제 UID 위치는 리더기 응답 구조에 따라 수정 필요
            return data.hex().upper()
        return None

    def close(self):
        """
        시리얼 포트를 닫습니다. 프로그램 종료 시 호출 권장.
        """
        self.ser.close()
