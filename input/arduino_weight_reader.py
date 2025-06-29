from input.arduino_rfid_reader import handle_rfid_data

def handle_weight_data(ser_weight, ser_rfid, tts):

    while True:
        line = ser_weight.readline().decode().strip()
        if line.startswith("WEIGHT1:"):
            try:
                action = line.split(":")[1]
            except ValueError:
                continue  # 잘못된 명령 무시

            if action == "ADD":
                print("무게1 증가")
                ser_rfid.write(b"RFID1_READ_ADD\n")
                ser_rfid.flush()
                handle_rfid_data(ser_rfid, tts)
            elif action == "REMOVE":
                print("무게1 감소")
                ser_rfid.write(b"RFID1_READ_REMOVE\n")
                ser_rfid.flush()
                handle_rfid_data(ser_rfid, tts)
            
        elif line.startswith("WEIGHT2:"):
            try:
                action = line.split(":")[1]
            except ValueError:
                continue  # 잘못된 명령 무시

            if action == "ADD":
                print("무게2 증가")
                ser_rfid.write(b"RFID2_READ_ADD\n")
                ser_rfid.flush()
                handle_rfid_data(ser_rfid, tts)
            elif action == "REMOVE":
                print("무게2 감소")
                ser_rfid.write(b"RFID2_READ_REMOVE\n")
                ser_rfid.flush()
                handle_rfid_data(ser_rfid, tts)