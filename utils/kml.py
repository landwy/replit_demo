
import simplekml


def read_pos_file(pos_file):
    """读取 .pos 文件，提取经纬度和高度信息"""
    coordinates = []
    with open(pos_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('%'):  # 跳过注释行
                continue
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            try:
                lat, lon, height = float(parts[2]), float(parts[3]), float(parts[4])
                coordinates.append((lon, lat, height))
            except ValueError:
                continue
    return coordinates


def create_kml_with_simplekmle(coordinates, output_file):
    """使用 simplekml 生成包含轨迹线和航点的 KML 文件"""
    kml = simplekml.Kml()

    # 创建轨迹（折线）
    linestring = kml.newlinestring(
        name="Trajectory",
        coords=coordinates
    )
    linestring.altitudemode = simplekml.AltitudeMode.clamptoground  # 绝对高度模式
    linestring.extrude = 1  # 轨迹线延伸到地面
    linestring.style.linestyle.color = simplekml.Color.yellow  # 轨迹线颜色
    linestring.style.linestyle.width = 1  # 线条宽度

    # 创建航点（每隔一定步长添加一个）
    step = max(1, len(coordinates) // 10)  # 让点的数量适中，避免过多
    for i, (lon, lat, height) in enumerate(coordinates[::step]):
        pnt = kml.newpoint(
            name=f"Point {i}",
            coords=[(lon, lat, height)]
        )
        pnt.altitudemode = simplekml.AltitudeMode.clamptoground
        pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"  # 设置标记图标

    kml.save(output_file)
    print(f"KML 文件已生成: {output_file}")


def main():
    pos_file = "F:\\GNSSdata\\RTKLIB\\RTKLIB-rtklib_2.4.3\\test\\spp-kf1.pos"  # 替换为你的 .pos 文件路径
    kml_file = "F:\\GNSSdata\\RTKLIB\\RTKLIB-rtklib_2.4.3\\trajectory.kml"  # 输出的 KML 文件路径

    coordinates = read_pos_file(pos_file)
    if not coordinates:
        print("未找到有效的坐标数据！")
        return

    create_kml_with_simplekmle(coordinates, kml_file)


if __name__ == "__main__":
    main()
