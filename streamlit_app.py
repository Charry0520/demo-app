import streamlit as st
import pandas as pd
import pydeck as pdk

# 读取CSV文件内容
def read_csv_data(file_path):
    return pd.read_csv(file_path)

# 根据选择的日期筛选数据
def filter_data_by_date(data, selected_date):
    return data[data['day'] == selected_date]

# 构建地图上的散点图层数据（标记地点）
def create_scatter_layer(data):
    locations = []
    for _, row in data.iterrows():
        start_lat, start_lon = row['start_latitude'], row['start_longitude']
        end_lat, end_lon = row['end_latitude'], row['end_longitude']
        desc = row['description']
        locations.extend([(start_lat, start_lon, desc), (end_lat, end_lon, desc)])

    return pdk.Layer(
        "ScatterplotLayer",
        locations,
        get_position=["lng", "lat"],
        get_radius=500,
        get_fill_color=[255, 165, 0],  # 更改标记颜色为橙色，可根据喜好调整RGB值
        get_text="text",
        pickable=True
    )

# 构建地图上的弧线图层数据（表示行程路线）
def create_arc_layer(data):
    arcs = []
    for _, row in data.iterrows():
        start_lat, start_lon = row['start_latitude'], row['start_longitude']
        end_lat, end_lon = row['end_latitude'], row['end_longitude']
        arcs.append({
            "sourcePosition": [start_lon, start_lat],
            "targetPosition": [end_lon, end_lat],
            "width": 3,
            "color": [0, 128, 255],  # 更改弧线颜色为浅蓝色，可根据喜好调整RGB值
            "text": row['transportation']
        })
    return pdk.Layer(
        "ArcLayer",
        arcs,
        get_source_position="sourcePosition",
        get_target_position="targetPosition",
        get_width="width",
        get_color="color",
        get_text="text",
        pickable=True
    )

# 主函数，整合构建可视化
def main():
    data = read_csv_data(r"./trip.csv")
    st.title("行程数据可视化")

    # 获取所有的日期列表并去重
    all_dates = data['day'].unique()

    # 设置页面整体样式，让内容可以合理分布，这里添加了一些内边距
    st.markdown("""
        <style>
          .main > div {
                padding-left: 2rem;
                padding-right: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # 使用两列布局，左侧放日期选择，右侧放地图，并添加适当的间距
    col1, col2 = st.columns([1, 3], gap="large")
    with col1:
        st.markdown("### 选择日期：")
        for date in all_dates:
            if st.button(date):
                selected_date = date
                # 根据选择的日期筛选数据
                selected_data = filter_data_by_date(data, selected_date)

                scatter_layer = create_scatter_layer(selected_data)
                arc_layer = create_arc_layer(selected_data)
                view_state = pdk.ViewState(
                    latitude=34.5,
                    longitude=135.3,
                    zoom=8,
                    pitch=40
                )
                r = pdk.Deck(
                    layers=[scatter_layer, arc_layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{sourcePosition} -> {targetPosition}"}
                )

    with col2:
        if 'r' in locals():  # 判断地图对象是否已创建（即是否有日期被点击选择）
            # 设置地图背景颜色为白色，使其更清晰
            r.map_style = "mapbox://styles/mapbox/light-v10"
            st.pydeck_chart(r)

if __name__ == "__main__":
    main()