import pcap
import dpkt
import keyboard
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.artist import Artist

# 설정된 MAC 주소
selected_mac = 'b827ebf1303d'
show_packet_length = 100
GAP_PACKET_NUM = 20
BANDWIDTH = 20
NSUB = int(BANDWIDTH * 3.2)

# 원하는 subcarrier 인덱스 리스트 (예: 20번째, 40번째, 60번째 subcarrier 선택)
selected_subcarrier_indices = [19, 39, 59]  # 인덱스는 0부터 시작

# 숫자를 특정 소수점 이하로 자르는 함수
def truncate(num, n):
    integer = int(num * (10 ** n)) / (10 ** n)
    return float(integer)

def sniffing(nicname, mac_address):
    print('Start Sniffing... @', nicname, 'UDP, Port 5500')
    sniffer = pcap.pcap(name=nicname, promisc=True, immediate=True, timeout_ms=50)
    sniffer.setfilter('udp and port 5500')

    before_ts = 0.0

    # 실시간 플롯 설정
    x = np.arange(0, show_packet_length, 1)
    y_list = [[0 for _ in range(0, show_packet_length)] for _ in selected_subcarrier_indices]

    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 8))

    line_list = []
    for y in y_list:
        line, = ax.plot(x, y, alpha=0.5)
        line_list.append(line)

    plt.title('{}'.format(selected_mac), fontsize=18)
    plt.ylabel('Signal Amplitude', fontsize=16)
    plt.xlabel('Packet', fontsize=16)
    plt.ylim(0, 1500)

    # Amp Min-Max gap 텍스트 초기화
    txt = ax.text(40, 1600, 'Amp Min-Max Gap: None', fontsize=14)
    gap_count = 0
    minmax = []

    idx = show_packet_length - 1

    for ts, pkt in sniffer:
        if int(ts) == int(before_ts):
            cur_ts = truncate(ts, 1)
            bef_ts = truncate(before_ts, 1)
            if cur_ts == bef_ts:
                before_ts = ts
                continue

        eth = dpkt.ethernet.Ethernet(pkt)
        ip = eth.data
        udp = ip.data

        # MAC 주소 추출
        mac = udp.data[4:10].hex()
        if mac != mac_address:
            continue

        # CSI 데이터 추출
        csi = udp.data[18:]
        csi_np = np.frombuffer(csi, dtype=np.int16, count=NSUB * 2)
        csi_np = csi_np.reshape((1, NSUB * 2))
        csi_cmplx = np.fft.fftshift(csi_np[:1, ::2] + 1.j * csi_np[:1, 1::2], axes=(1,))
        csi_data = list(np.abs(csi_cmplx)[0])

        # 선택된 subcarrier 데이터 추출 및 플롯 업데이트
        idx += 1
        for i, subcarrier_index in enumerate(selected_subcarrier_indices):
            selected_subcarrier_value = csi_data[subcarrier_index]
            del y_list[i][0]
            y_list[i].append(selected_subcarrier_value)
            line_list[i].set_xdata(x)
            line_list[i].set_ydata(y_list[i])

            # Min-Max Gap 계산
            if gap_count == 0:
                if len(minmax) <= i:
                    minmax.append([selected_subcarrier_value, selected_subcarrier_value])
                else:
                    minmax[i] = [selected_subcarrier_value, selected_subcarrier_value]
            else:
                minmax[i][0] = min(minmax[i][0], selected_subcarrier_value)
                minmax[i][1] = max(minmax[i][1], selected_subcarrier_value)

        gap_list = [mm[1] - mm[0] for mm in minmax]
        gap = max(gap_list)
        Artist.remove(txt)
        txt = ax.text(40, 1600, 'Amp Min-Max Gap: {}'.format(gap), fontsize=14)
        gap_count += 1
        if gap_count == GAP_PACKET_NUM:
            gap_count = 0
            minmax = []

        fig.canvas.draw()
        fig.canvas.flush_events()
        before_ts = ts

        if keyboard.is_pressed('s'):
            print("Stop Collecting...")
            exit()

if __name__ == '__main__':
    sniffing('wlan0', selected_mac)