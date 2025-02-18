import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy.stats import norm, shapiro, ks_2samp, kurtosis, skew

# Configuración del título y estilo
st.set_page_config(page_title="Análisis de Anchura del Esternón", layout="wide")
st.markdown("# 📊 Análisis de Anchura del Esternón")
st.markdown(
    "Este Dashboard permite visualizar la distribución de anchuras del esternón y detectar anomalías en los datos. 🔍")

# 📂 Subida de archivo Excel
archivo = st.file_uploader("📂 Sube el archivo Excel con los datos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo, header=1)

    # 📌 Definir nombres de las columnas relevantes
    anchura_min = "b(sternal Thickness)MIN"
    anchura_max = "MAX"
    columnas_requeridas = [anchura_max, anchura_min]

    if not all(col in df.columns for col in columnas_requeridas):
        st.error(f"🚨 El archivo debe contener las columnas: {columnas_requeridas}")
    else:
        # 🧮 Cálculo de métricas
        df["Anchura Media (mm)"] = (df[anchura_max] + df[anchura_min]) / 2
        df["Diferencia entre la anchura máxima y mínima (mm)"] = df[anchura_max] - df[anchura_min]

        # 📊 Estadísticas clave
        media = df["Anchura Media (mm)"].mean()
        desviacion = df["Anchura Media (mm)"].std()
        min_anchura = df["Anchura Media (mm)"].min()
        max_anchura = df["Anchura Media (mm)"].max()
        asimetria = skew(df["Anchura Media (mm)"].dropna())
        curtosis_val = kurtosis(df["Anchura Media (mm)"].dropna())

        # 📌 Cálculo de percentiles
        df["Anchura Media (mm)"] = df["Anchura Media (mm)"].astype(str).str.strip()
        df["Anchura Media (mm)"] = pd.to_numeric(df["Anchura Media (mm)"], errors="coerce")

        if df["Anchura Media (mm)"].count() > 0:
            percentiles = np.percentile(df["Anchura Media (mm)"].dropna(), [5, 50, 95])
        else:
            percentiles = [np.nan, np.nan, np.nan]


        # 📌 Pruebas de normalidad
        stat_shapiro, p_shapiro = shapiro(df["Anchura Media (mm)"].dropna())
        stat_ks, p_ks = ks_2samp(df["Anchura Media (mm)"].dropna(), np.random.normal(media, desviacion, len(df)))

        # 📌 Superposición del histograma real con la curva normal
        fig_hist = px.histogram(df, x="Anchura Media (mm)", nbins=20, title="Superposición del histograma de la anchura media con la curva normal", opacity=0.6,
                                marginal="box")
        x = np.linspace(media - 3 * desviacion, media + 3 * desviacion, 100)
        y = norm.pdf(x, media, desviacion) * len(df) * (
                    df["Anchura Media (mm)"].max() - df["Anchura Media (mm)"].min()) / 20
        fig_hist.add_scatter(x=x, y=y, mode='lines', name="Curva Normal")

        # 📌 Mostrar estadísticas
        st.markdown("### 📌 Estadísticas Clave")
        col1, col2, col3 = st.columns(3)
        col1.metric("📏 Media de Anchura", f"{media:.2f} mm")
        col2.metric("📉 Desviación Estándar", f"{desviacion:.2f} mm")
        col3.metric("📈 Asimetría", f"{asimetria:.2f}")

        col4, col5, col6 = st.columns(3)
        col4.metric("🔼 Máxima Anchura", f"{max_anchura:.2f} mm")
        col5.metric("🔽 Mínima Anchura", f"{min_anchura:.2f} mm")
        col6.metric("🔄 Curtosis", f"{curtosis_val:.2f}")
        st.write("·**Desviación Estándar**: mide cuánto varían los datos respecto a la media. Es decir, indica si los valores están muy dispersos o concentrados cerca del promedio. (**(cercana a 0)** → Datos muy agrupados alrededor de la media, poca variabilidad en las anchuras del esternón., , **Alta** →  Datos muy dispersos respecto a la media, mayor variabilidad en las anchuras del esternón")
        st.write("·**Asimetría**: mide cuán simétrica es la distribución de los datos respecto a la media. ( ·**0** → Distribución simétrica, como la normal,    ·**Negativo (< 0)** → Sesgo a la izquierda (cola más larga a la izquierda, la distribución tiene más valores menores a la media),   ·**Positivo (> 0)** → Sesgo a la derecha (cola más larga a la derecha, la distribución tiene más valores mayores a la media)).")
        st.write("·**Curtosis**: mide si los datos tienen colas más o menos pesadas en comparación con una distribución normal. (**0 o cercano a 0** → Mesocúrtica (Distribución normal, colas estándar)., **Negativo (< 0)** → Platicúrtica (Colas ligeras, distribución más plana, datos más dispersos, sin valores extremos), **Positivo (> 0)** → Leptocúrtica (Colas pesadas, picos más pronunciados, es decir, muchos valores extremos, lo que sugiere casos atípicos (outliers))). ")


        # 📌 Interpretar desviación
        def interpretar_desviacion(media, desviacion):
            rango_68 = (media - desviacion, media + desviacion)
            rango_95 = (media - 2 * desviacion, media + 2 * desviacion)
            rango_997 = (media - 3 * desviacion, media + 3 * desviacion)

            st.markdown("### 📌 Interpretación de la Desviación Estándar")
            st.write(
                f"🔹 **El 68% de los pacientes** tienen una anchura entre **{rango_68[0]:.2f} mm** y **{rango_68[1]:.2f} mm**.")
            st.write(
                f"🔹 **El 95% de los pacientes** tienen una anchura entre **{rango_95[0]:.2f} mm** y **{rango_95[1]:.2f} mm**.")
            st.write(
                f"🔹 **El 99.7% de los pacientes** tienen una anchura entre **{rango_997[0]:.2f} mm** y **{rango_997[1]:.2f} mm**.")

            # Evaluación del impacto en el diseño del implante
            if desviacion < 3:
                st.success(
                    "✅ La desviación estándar es baja, lo que indica que las anchuras son muy similares entre los pacientes. Esto permite diseñar un implante con medidas estándar.")
            elif 3 <= desviacion <= 7:
                st.warning(
                    "⚠️ La desviación estándar es moderada, lo que sugiere cierta variabilidad en las anchuras del esternón. Puede ser útil considerar algunas opciones de tamaño.")
            else:
                st.error(
                    "🚨 La desviación estándar es alta, lo que indica una gran variabilidad en las anchuras del esternón. Podría ser necesario diseñar implantes personalizados para diferentes grupos de pacientes.")


        interpretar_desviacion(media, desviacion)


        # 📌 Mostrar percentiles
        st.markdown("### 📌 Percentiles de Anchura Media")
        col7, col8, col9 = st.columns(3)
        col7.metric("🔹 Percentil 5%", f"{percentiles[0]:.2f} mm")
        col8.metric("🔸 Mediana (50%)", f"{percentiles[1]:.2f} mm")
        col9.metric("🔹 Percentil 95%", f"{percentiles[2]:.2f} mm")
        st.write(
            "·Los **percentiles** permiten evaluar la distribución de las anchuras medias del esternón en la población analizada. El percentil 5% indica el valor por debajo del cual se encuentran el 5% de los datos, la mediana (50%) representa el valor central de la distribución, y el percentil 95% muestra el valor por debajo del cual se encuentra el 95% de la población.")

        # Gráfico de distribución de anchura media
        fig1 = px.histogram(df, x="Anchura Media (mm)", nbins=20, title="Distribución de Anchura Media")
        st.plotly_chart(fig1)

        # 🔍 Filtrar valores de anchura media interactivamente
        min_slider, max_slider = st.slider(
            "📏 Selecciona un rango de anchura media para visualizar:",
            float(df["Anchura Media (mm)"].min()),
            float(df["Anchura Media (mm)"].max()),
            (float(df["Anchura Media (mm)"].min()), float(df["Anchura Media (mm)"].max()))
        )

        df_filtrado = df[(df["Anchura Media (mm)"] >= min_slider) & (df["Anchura Media (mm)"] <= max_slider)]
        st.write(f"🔎 Filtrando esternones con anchura entre **{min_slider:.2f} mm** y **{max_slider:.2f} mm**")

        fig_filtrado = px.histogram(df_filtrado, x="Anchura Media (mm)", nbins=20,
                                    title=f"Distribución Filtrada ({min_slider:.2f} - {max_slider:.2f} mm)")
        st.plotly_chart(fig_filtrado)



        # 📈 Histogramas interactivos
        if st.checkbox("📉 Mostrar variabilidad entre anchura máxima y mínima"):
            fig2 = px.box(df, y="Diferencia entre la anchura máxima y mínima (mm)",
                          title="Variabilidad entre Anchura Máxima y Mínima")
            st.plotly_chart(fig2)


        # 📌 Resultados de las pruebas de normalidad
        st.markdown("### 🧪 Pruebas de Normalidad")
        st.write(f"**Shapiro-Wilk test**: Estadístico = {stat_shapiro:.4f}, p-valor = {p_shapiro:.4f}")
        st.write(f"**Kolmogorov-Smirnov test**: Estadístico = {stat_ks:.4f}, p-valor = {p_ks:.4f}")

        if p_shapiro < 0.05:
            st.warning("🚨 Los datos NO siguen una distribución normal según el test de Shapiro-Wilk (p < 0.05)")
        else:
            st.success("✅ Los datos parecen seguir una distribución normal según el test de Shapiro-Wilk (p >= 0.05)")

        if p_ks < 0.05:
            st.warning("🚨 Los datos NO siguen una distribución normal según el test de Kolmogorov-Smirnov (p < 0.05)")
        else:
            st.success(
                "✅ Los datos parecen seguir una distribución normal según el test de Kolmogorov-Smirnov (p >= 0.05)")

        st.plotly_chart(fig_hist)


        # 📌 Análisis de valores extremos
        st.markdown("### 🚨 Detección de Errores en la Base de Datos")
        df["Diferencia entre la anchura máxima y mínima (mm)"] = df["Diferencia entre la anchura máxima y mínima (mm)"].astype(float)

        errores = df[df[anchura_min] > df[anchura_max]]
        errores2 = df[df["Diferencia entre la anchura máxima y mínima (mm)"] >= 8]

        if not errores.empty:
            st.warning(f"⚠️ Se encontraron {len(errores)} registros con anchura mínima mayor que la máxima:")
            st.write(errores)

        if not errores2.empty:
            st.warning(f"⚠️ Se encontraron {len(errores2)} registros con diferencias de anchura mayores a 8 mm:")
            st.write(errores2)

        # 📌 Casos con anchura media < 4 mm
        errores3 = df[df["Anchura Media (mm)"] <= 4]
        if not errores3.empty:
            st.error(f"⚠️ Se encontraron {len(errores3)} registros con anchura media < 4 mm:")
            st.write(errores3)


        st.success("🎉 Análisis completado. Puedes ajustar los filtros para explorar más datos.")




