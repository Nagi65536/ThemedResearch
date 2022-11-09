import config as cf


def communication(car_id, start_node, goal_node, delay=-1) -> bool:
    try:
        # 接続報告-送信
        send_data: bytes = get_encode_data(
            'connect', car_id, tag_id, destination)
        sock.send(send_data)

        # 指示-受信
        get_data = None
        while not get_data:
            if car_id in recv_datum:
                get_data = recv_datum.pop(car_id)
            time.sleep(PROCESS_DELAY)

        print(f'{car_id} > {get_data["operate"]}')

        if get_data['operate'] == 'stop':
            # 進入指示-受信
            get_data = None
            while not get_data:
                if car_id in recv_datum:
                    get_data = recv_datum.pop(car_id)
                time.sleep(PROCESS_DELAY)
            print(f'{car_id} > {get_data["operate"]}')

        print(f'{car_id} 通過中')
        time.sleep(delay)

        # 通過済報告-送信
        send_data: bytes = get_encode_data(
            'passed', car_id, 'tag_s_passed_000_id', destination)
        sock.send(send_data)
        print(f'{car_id} < passed')

        return True
    except:
        print('【ERROR】')
        return False
