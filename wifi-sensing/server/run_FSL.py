import socketserver
import matplotlib.pyplot as plt
import numpy as np
import torch
import pandas as pd
import pickle
import torch.nn.functional as F
from os.path import exists
# from dataloader.dataset import FSLDataset  # 주석 처리
from runner.utils import get_config, extract_test_sample
from model.vit import ViT
import runner.proto as proto

config = get_config('config.yaml')
use_cuda = False  # CUDA 사용 안 함으로 변경

HOST = config['application']['server']['ip']
PORT = config['application']['server']['port']

mac = config['application']['client']['mac']

global P_COUNT
P_COUNT = 0
window_size = config['FSL']['dataset']['window_size']
num_sub = config['subcarrier'][config['application']['client']["bandwidth"]]
activities = config['application']['client']["activity_labels"]

columns = []
for i in range(0, num_sub):
    columns.append('_' + str(i))

null_pilot_col_list = ['_' + str(x + 32) for x in [-32, -31, -30, -29, -21, -7, 0, 7, 21, 29, 30, 31]]

print('======> Load model')
model = proto.load_protonet_vit(
        in_channels=config['application']['model']['ViT']["in_channels"],
        patch_size=(config['application']['model']['ViT']["patch_size"], config['subcarrier'][config['application']['client']["bandwidth"]]),
        embed_dim=config['application']['model']['ViT']["embed_dim"],
        num_layers=config['application']['model']['ViT']["num_layers"],
        num_heads=config['application']['model']['ViT']["num_heads"],
        mlp_dim=config['application']['model']['ViT']["mlp_dim"],
        num_classes=len(config['application']['client']["activity_labels"]),
        in_size=[config['application']['client']["window_size"], config['subcarrier'][config['application']['client']["bandwidth"]]]
        )
    
model.load_state_dict(torch.load(config['application']['FSL']['save_model_path']))

if use_cuda:
    model.to(config['GPU']['gpu_ids'][0])
print('======> Success')

print('======> Create Prototypes')
n_way = config['FSL']['test']['n_way']
n_support = config['FSL']['test']['n_support']
n_query = config['FSL']['test']['n_query']

from dataloader.dataset import FSLDataset  # 필요한 곳에서 임포트

support_data = FSLDataset(config['FSL']['dataset']['test_dataset_path'],
                          win_size=window_size,
                          mode='test', 
                          mac=False, time=False
                          )
support_x, support_y = support_data.data_x, support_data.data_y
support_x = np.expand_dims(support_x, axis=1)
support_sample = extract_test_sample(n_way, n_support, n_query, support_x, support_y, config)
z_proto = model.create_protoNet(support_sample)
print('======> Success')

mac_dict = {}
mac_dict[mac] = pd.DataFrame(columns=columns)

class MyTcpHandler(socketserver.BaseRequestHandler):

    def handle(self):
        buffer = self.request.recv(2048)  # receive data
        buffer = pickle.loads(buffer)
        global P_COUNT
        P_COUNT += 1

        if not buffer:
            print("Fail to receive!")
            return
        else:
            csi_df = pd.DataFrame([buffer], columns=columns)

            try:
                mac_dict[mac] = pd.concat([mac_dict[mac], csi_df], ignore_index=True)
                if len(mac_dict[mac]) == window_size and P_COUNT == window_size:
                    c_data = np.array(mac_dict[mac])
                    c_data = torch.from_numpy(c_data).unsqueeze(0).float()
                    
                    with torch.no_grad():
                        output = model.proto_test(c_data, z_proto, n_way, 0)
                        y_hat = output['y_hat']

                    print('Predict result: {}'.format(activities[y_hat.item()]))
                    self.request.sendall(pickle.dumps(activities[y_hat.item()]))


                    mac_dict[mac].drop(0, inplace=True)
                    mac_dict[mac].reset_index(drop=True, inplace=True)

                    P_COUNT = 0

                elif len(mac_dict[mac]) == window_size and P_COUNT == window_size//2:
                    c_data = np.array(mac_dict[mac])
                    c_data = torch.from_numpy(c_data).unsqueeze(0).float()

                    with torch.no_grad():
                        output = model.proto_test(c_data, z_proto, n_way, 0)
                        y_hat = output['y_hat']

                    print('Predict result: {}'.format(activities[y_hat.item()]))
                    self.request.sendall(pickle.dumps(activities[y_hat.item()]))


                    mac_dict[mac].drop(0, inplace=True)
                    mac_dict[mac].reset_index(drop=True, inplace=True)

                    P_COUNT = 0

                elif len(mac_dict[mac]) == window_size:
                    mac_dict[mac].drop(0, inplace=True)
                    mac_dict[mac].reset_index(drop=True, inplace=True)

                elif len(mac_dict[mac]) > window_size:
                    print("Error!")

            except Exception as e:
                print('Error', e)

def runServer(HOST, PORT):
    print('==== Start Edge Server ====')
    print('==== Exit with Ctrl + C ====')

    try:
        server = socketserver.TCPServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()

    except KeyboardInterrupt:
        print('==== Exit Edge server ====')

if __name__ == '__main__':
    runServer(HOST, PORT)
