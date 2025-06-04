last_weight1 = 0
last_weight2 = 0
THRESHOLD = 100  # 100g 이상 변화 시 판단

def handle_weight_data(ser_weight, ser_rfid):
    global last_weight1
    global last_weight2

    while True:
        line = ser_weight.readline().decode().strip()
        if line.startswith("WEIGHT1:"):
            try:
                current_weight = int(line.split(":")[1])
            except ValueError:
                continue  # 잘못된 숫자 무시

            if last_weight1 is not None:
                delta = current_weight - last_weight1
                print(f"무게 변화량: {delta}g")

                if delta > THRESHOLD:
                    print("📦 무게 증가 → RFID에 READ_ADD 요청")
                    ser_rfid.write(b"RFID1_READ_ADD\n")
                    ser_rfid.flush()

                elif delta < -THRESHOLD:
                    print("📤 무게 감소 → RFID에 READ_REMOVE 요청")
                    ser_rfid.write(b"RFID1_READ_REMOVE\n")
                    ser_rfid.flush()

            last_weight1 = current_weight
            
        elif line.startswith("WEIGHT2:"):
            try:
                current_weight = int(line.split(":")[1])
            except ValueError:
                continue  # 잘못된 숫자 무시

            if last_weight2 is not None:
                delta = current_weight - last_weight2
                print(f"무게 변화량: {delta}g")

                if delta > THRESHOLD:
                    print("📦 무게 증가 → RFID에 READ_ADD 요청")
                    ser_rfid.write(b"RFID1_READ_ADD\n")
                    ser_rfid.flush()

                elif delta < -THRESHOLD:
                    print("📤 무게 감소 → RFID에 READ_REMOVE 요청")
                    ser_rfid.write(b"RFID1_READ_REMOVE\n")
                    ser_rfid.flush()

            last_weight2 = current_weight