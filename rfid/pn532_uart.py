import serial
import time

class PN532UART:
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5):
        """
        PN532 리더기를 UART(시리얼)로 초기화합니다.

        Args:
            port (str): UART 포트 경로 (예: '/dev/serial0')
            baudrate (int): 통신 속도 (기본값 9600)
            timeout (float): 수신 대기 시간 (초 단위)
        """
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(1.0)  # 포트 연결 후 안정화 시간 확보

    def read_uid(self) -> str | None:
        """
        PN532 리더기로부터 카드 UID를 읽습니다.

        Returns:
            UID 문자열 (예: '04A1BC3D12') 또는 읽은 게 없으면 None
        """
        self.ser.write(b'\x55')  # 이 부분은 실제 PN532 명령으로 교체 필요
        time.sleep(0.2)  # 응답 대기

        if self.ser.in_waiting:
            data = self.ser.read(self.ser.in_waiting)  # 버퍼에 있는 응답 읽기
            uid = self._extract_uid(data)  # UID 추출 함수 호출
            return uid
        

        return None  # 응답 없으면 None 반환

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
