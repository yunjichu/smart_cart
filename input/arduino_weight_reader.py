last_weight = 0
THRESHOLD = 100  # 100g 이상 변화 시 판단

def handle_weight_data(ser_weight, ser_rfid):
    global last_weight

    while True:
        line = ser_weight.readline().decode().strip()
        if line.startswith("WEIGHT:"):
            try:
                current_weight = int(line.split(":")[1])
            except ValueError:
                continue  # 잘못된 숫자 무시

            if last_weight is not None:
                delta = current_weight - last_weight
                print(f"무게 변화량: {delta}g")

                if delta > THRESHOLD:
                    print("📦 무게 증가 → RFID에 READ_ADD 요청")
                    ser_rfid.write(b"READ_ADD\n")

                elif delta < -THRESHOLD:
                    print("📤 무게 감소 → RFID에 READ_REMOVE 요청")
                    ser_rfid.write(b"READ_REMOVE\n")

            last_weight = current_weight
