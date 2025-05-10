import serial
import time

class PN532UART:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(1.0)
        self.ser.reset_input_buffer()

    def read_uid(self):
        try:
            # PN532 UART 프레임: InListPassiveTarget 명령 (ISO14443A)
            # 참고: 이프레임은 Host-to-PN532 (extended frame)
            cmd = bytes([
                0x00, 0x00, 0xFF, 0x04, 0xFC,
                0xD4, 0x4A, 0x01, 0x00,
                0xE1, 0x00
            ])

            self.ser.write(cmd)
            time.sleep(0.1)

            response = self.ser.read(32)
            print("[DEBUG] response:", response.hex())


            # 응답 프레임 최소 길이 확인
            if len(response) >= 24:
                uid_len = response[23]
                uid = response[24:24 + uid_len]
                return uid.hex().upper()

            return None

        except Exception as e:
            print("UID 읽기 오류:", e)
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
