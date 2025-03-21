
import numpy as np
import logging

def parse_satellite_data(filename):
    """
    Parse satellite data from TXT file.
    Returns: Dictionary with epoch times as keys and satellite data as values.
    """
    satellite_data = {}
    current_epoch = None

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('time'):
                current_epoch = line.split(' ', 1)[1]  # Extract timestamp after 'time '
                satellite_data[current_epoch] = []
                logging.info(f"Processing epoch {current_epoch}")
            else:
                data = line.split()
                if current_epoch and len(data) >= 7 and float(data[0]) != 0:  # Ensure valid satellite data
                    sat_data = {
                        'X': float(data[0]),
                        'Y': float(data[1]),
                        'Z': float(data[2]),
                        'SNR': float(data[3]),
                        'satellite_id': data[4],
                        'azimuth': float(data[5]),  # Ensure float conversion
                        'elevation': float(data[6]),
                    }
                    satellite_data[current_epoch].append(sat_data)
                    logging.debug(f"Added satellite {data[4]} with SNR {data[3]}")

    logging.info(f"Total epochs processed: {len(satellite_data)}")
    return satellite_data


def compute_dop(satellites):
    """
    Compute HDOP and GDOP given a list of (azimuth, elevation) pairs.
    Returns: (HDOP, GDOP)
    """
    if len(satellites) < 4:
        return float('inf'), float('inf')  # Not enough satellites for DOP calculation

    azimuths = [s[0] for s in satellites] # Convert to radians
    elevations =[s[1] for s in satellites]

    A = np.array([
        [np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e), 1]
        for a, e in zip(azimuths, elevations)
    ])

    cond_number = np.linalg.cond(A.T @ A)
    if cond_number > 1e12:  # Avoid singular matrix issues
        logging.warning(f"High condition number {cond_number}, results may be unreliable")
        return float('inf'), float('inf')

    Q = np.linalg.inv(A.T @ A)
    GDOP = np.sqrt(np.trace(Q))
    HDOP = np.sqrt(Q[0, 0] + Q[1, 1])

    return HDOP, GDOP


# 📌 读取数据并计算 DOP
filename = "..\\files\\satpos1.txt"  # 替换为你的文件名
satellite_data = parse_satellite_data(filename)

print("Total epochs:", len(satellite_data))

for epoch, satdata in satellite_data.items():
    satellites = [(d['azimuth'], d['elevation']) for d in satdata]
    hdop, gdop = compute_dop(satellites)
    print(f"Epoch {epoch}: HDOP = {hdop:.3f}, GDOP = {gdop:.3f}")
