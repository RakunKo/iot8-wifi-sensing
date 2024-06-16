## IoT8 Wifi Sensing

### Project Proposal

We started the project with the goal of analyzing CSI using Raspberry Pi and wifi CSI and finding out human movements through analysis.

### Setting

- Raspberry Pi 4 (monitoring CSI)
- Raspberry Pi 3 (AP mode)
- Python 3.8.19
- Pytorch
  
<img width="489" alt="스크린샷 2024-05-30 오후 2 56 53" src="https://github.com/RakunKo/iot8/assets/145656942/84021b10-23ff-447f-be21-27937d36b655">

### CSI extract

- Using Nexmon CSI extractor

### CSI Visualization

- we preprocess to Lowpass, Hanpel filter, and select appropriate subcarrier. 

<img width="1312" alt="스크린샷 2024-05-25 오후 1 40 28" src="https://github.com/RakunKo/iot8/assets/145656942/75bd6bfa-9f25-4460-8422-71f2f0fab694">

### Motion Detect

- Receive preprocessed CSI data using DL and derive appropriate actions
- Training model...
<img width="907" alt="스크린샷 2024-06-16 오후 1 46 11" src="https://github.com/RakunKo/iot8/assets/145656942/52ed699d-76bb-4b79-98a5-0d2293a91df4">

- Result...
  
![IMG_1363](https://github.com/RakunKo/iot8/assets/145656942/6c35b1c4-4e14-4873-9cf9-cad9d2f033c4)


### Referenced Projects

- CSI extractor Tool : Nexmon CSI
  https://github.com/seemoo-lab/nexmon_csi

- Convert Pacp to CSV file Tool
  https://github.com/cheeseBG/pcap-to-csv

- CSI Visualization Tool
  https://github.com/cheeseBG/csi-visualization

- Wifi sensing
  https://github.com/oss-inc/mowa-wifi-sensing

### Referenced Paper, Page

- WiFi Sensing with Channel State Information: A Survey(YONGSEN MA, GANG ZHOU, and SHUANGQUAN WANG, Computer Science Department, College of William & Mary, USA)
  
- Channel State Information from Pure Communication to Sense and Track Human Motion: A Survey(Mohammed A. A. Al-qaness 1 , Mohamed Abd Elaziz 2 , Sunghwan Kim 3,* , Ahmed A. Ewees 4, Aaqif Afzaal Abbasi 5, Yousif A. Alhaj 6 and Ammar Hawbani 7)
