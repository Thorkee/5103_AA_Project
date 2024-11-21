# Project Overview

This is a **collaborative project** with the **Hong Kong Airport Authority** aimed at detecting potential issues when workers transport goods using trolleys. The system is designed to trigger an **alert** if the **height of the goods** on the trolley exceeds the height of the operator. Alerts are sent via **Telegram** to notify relevant personnel of any safety risks.

To test our model, you may call API Key: **mAG26LjDPqjrqmJOBrRs**, ver. 5.

## Key Components:

1. **Data Collection**:
   - Collected nearly **300GB of raw data** using a **RealSense RGB-D camera** at **Hong Kong International Airport**.

2. **RGB-D Footage Extraction**:
   - Extracted **RGB-D footage** from the **rosbag** files collected.
   - You can access the data [here on OneDrive](https://onedrive.live.com/?authkey=%21AOt0M8eEwptuXnM&id=F40A6C7EC7914BD9%2170009&cid=F40A6C7EC7914BD9).

3. **Data Labeling and Model Training**:
   - Labeled the data using **Roboflow**.
   - Followed this by **training the model** on the labeled dataset.

4. **Proximity Estimation**:
   - We need to devise an efficient method to **compare the heights** of goods on trolleys and the operators.
   - Options include:
     - Direct **calculation and comparison of numerical heights**.
     - Exploring **alternative methods** that might offer better accuracy or efficiency.

5. **Alert System Development**:
   - Developed a **Python script** to send alerts via **Telegram** using the **Telegram API**.
