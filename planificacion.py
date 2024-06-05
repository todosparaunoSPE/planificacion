# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 12:30:29 2024

@author: jperezr
"""


import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def calcular_ahorro_retiro(edad_actual, edad_retiro, ingreso_actual, tasa_interes):
    anos_inversion = edad_retiro - edad_actual
    ahorro_total = ingreso_actual * ((1 + tasa_interes)**anos_inversion)
    return ahorro_total

st.title("Calculadora de Planes de Ahorro para el Retiro")

edad_actual = st.slider("Edad actual:", min_value=18, max_value=100, value=30)
edad_retiro = st.slider("Edad de retiro:", min_value=edad_actual+1, max_value=100, value=65)
ingreso_actual = st.number_input("Ingreso mensual actual ($):", value=3000)
tasa_interes = st.slider("Tasa de interés anual (%):", min_value=0.0, max_value=20.0, value=5.0) / 100
anos_retiro = st.slider("Años de retiro:", min_value=1, max_value=50, value=20)

anos_inversion = edad_retiro - edad_actual
ahorro_total = calcular_ahorro_retiro(edad_actual, edad_retiro, ingreso_actual, tasa_interes)
ahorro_necesario = ingreso_actual * anos_retiro

st.write(f"Se necesitará un ahorro total de ${ahorro_necesario:,.2f} para el retiro.")
st.write(f"Con una tasa de interés del {tasa_interes*100}%, a la edad de retiro tendrás ahorrado ${ahorro_total:,.2f}.")

st.markdown("---")
st.subheader("Características Adicionales")
st.markdown("### Opciones de inversión")

tickers = st.text_input("Ingresa los tickers de los activos financieros separados por comas (ej: AAPL,MSFT,GOOGL)")

valor_total_proyectado = 0

if tickers:
    tickers_list = [ticker.strip() for ticker in tickers.split(",")]
    cantidades_invertidas = {}
    for ticker in tickers_list:
        cantidades_invertidas[ticker] = st.number_input(f"Inversión en {ticker} ($):", min_value=0, value=1000)

    rendimiento_anual = st.slider("Rendimiento anual esperado (%):", min_value=-10.0, max_value=20.0, value=7.0) / 100
    
    proyecciones = {}
    for ticker in tickers_list:
        # Limpiar la caché antes de obtener los datos
        @st.cache(allow_output_mutation=True)
        def get_data(ticker):
            return yf.download(ticker, period="5y")
        
        datos = get_data(ticker)
        if not datos.empty:
            precio_actual = datos["Close"][-1]
            cantidad_invertida = cantidades_invertidas[ticker]
            cantidad_tickers = cantidad_invertida / precio_actual
            valor_proyectado = cantidad_tickers * (precio_actual * ((1 + rendimiento_anual) ** anos_inversion))
            proyecciones[ticker] = (precio_actual, valor_proyectado)
            valor_total_proyectado += valor_proyectado
            
            # Plot
            plt.figure(figsize=(10, 6))
            plt.plot(datos.index, datos["Close"], label='Precio')
            plt.title(f"Precio de {ticker} en los últimos 5 años")
            plt.xlabel("Fecha")
            plt.ylabel("Precio (USD)")
            plt.legend()
            
            # Plot proyección
            anos = pd.date_range(start=datos.index[-1], periods=anos_inversion*12+1, freq='M')[1:]
            proyeccion = [precio_actual * ((1 + rendimiento_anual) ** (i+1)) for i in range(anos_inversion*12)]
            plt.plot(anos, proyeccion, label='Proyección', linestyle='--')
            plt.legend()
            
            st.pyplot()
        else:
            proyecciones[ticker] = (None, None)

    st.write("Proyección del valor de los activos financieros a la edad de retiro:")
    for ticker, valores in proyecciones.items():
        precio_actual, valor_proyectado = valores
        if precio_actual is not None:
            st.write(f"**{ticker}**: Precio actual: ${precio_actual:.2f},")
            st.write(f"    Valor proyectado en {anos_inversion} años: ${valor_proyectado:,.2f}")
        else:
            st.write(f"**{ticker}**: No se pudieron obtener datos.")

    st.write(f"**Valor total proyectado de todas las inversiones a la edad de retiro:** ${valor_total_proyectado:,.2f}")

total_ahorro_retiro = ahorro_total + valor_total_proyectado

#st.write(f"**El total ahorrado a la edad de retiro, incluyendo inversiones y contribuciones adicionales, será de:** ${total_ahorro_retiro:,.2f}")

with st.expander("Contribuciones adicionales"):
    contribucion_mensual = st.number_input("Contribución volunaraia mensual ($):", value=100)
    ahorro_contribuciones = contribucion_mensual * 12 * anos_inversion
    st.write(f"**Contribuciones voluntarias a lo largo de {anos_inversion} años:** ${ahorro_contribuciones:,.2f}")

    ahorro_total_contribuciones = total_ahorro_retiro + ahorro_contribuciones
    st.write(f"**Ahorro total con contribuciones adicionales e inversiones proyectadas:** ${ahorro_total_contribuciones:,.2f}")



