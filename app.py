import streamlit as st
import math
from geopy.distance import distance
from geopy.point import Point
import folium
from streamlit_folium import folium_static
import pandas as pd

st.title("Покрытие широкой области локальными областями")

# Поля для ввода
center_lat = st.text_input("Введите географическую широту центра (например, 55.7522)")
center_lon = st.text_input("Введите географическую долготу центра (например, 37.6156)")
R_big = st.text_input("Введите радиус области (в км)")
r = st.text_input("Введите радиус локальных областей (в км)")

# Проверка: введены ли все значения
if center_lat and center_lon and R_big and r:
    try:
        center_lat = float(center_lat)
        center_lon = float(center_lon)
        R_big = float(R_big)
        r = float(r)

        center_point = Point(center_lat, center_lon)
        dx = 2 * r
        dy = r * math.sqrt(3)

        max_i = int(R_big / dx) + 2
        max_j = int(R_big / dy) + 2

        circle_centers = []

        for j in range(-max_j, max_j + 1):
            for i in range(-max_i, max_i + 1):
                x_offset = i * dx + (r if j % 2 != 0 else 0)
                y_offset = j * dy
                dist_from_center = math.hypot(x_offset, y_offset)
                if dist_from_center > R_big:
                    continue
                azimuth = math.degrees(math.atan2(x_offset, y_offset)) % 360
                new_point = distance(kilometers=dist_from_center).destination(center_point, azimuth)
                circle_centers.append((new_point.latitude, new_point.longitude))

        # Карта
        m = folium.Map(location=[center_lat, center_lon], zoom_start=9)

        folium.Circle(
            location=[center_lat, center_lon],
            radius=R_big * 1000,
            color='blue',
            fill=False,
            weight=2,
            popup='Большой круг'
        ).add_to(m)

        for lat, lon in circle_centers:
            folium.Circle(
                location=[lat, lon],
                radius=r * 1000,
                color='green',
                fill=True,
                fill_opacity=0.3,
                weight=1
            ).add_to(m)

        folium_static(m)

        # Формируем вывод в формате: Номер:r km: Широта, Долгота
        formatted_coords = []
        for i, (lat, lon) in enumerate(circle_centers, start=1):
            formatted_coords.append(f"{i}:{r}km: {lat}, {lon}")

        # Создаём строку с результатом
        output_data = "\n".join(formatted_coords)
        
       # Кнопка для скачивания с нужным форматом
        st.download_button("Скачать координаты центров локальных областей(TXT)", output_data, file_name="координаты_центров.txt", mime="text/plain")

    except ValueError:
        st.error("Пожалуйста, введите корректные числовые значения.")
else:
    st.info("Введите значения в поля выше для построения карты.")
