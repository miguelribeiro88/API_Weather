import tkinter as tk
import requests
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import datetime

# Variáveis globais para armazenar dados climáticos anteriores
previous_temperature = None
previous_humidity = None
previous_wind_speed = None
previous_pressure = None

# Variável global para criar lista vazia de histórico
historical_data = []


# Função para obter informações sobre o clima da API
def get_weather(city):

    API_key = "6ed0c3d1a7f543cd53d44d19794ffd08"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
    res = requests.get(url)
    if res.status_code == 404:
        messagebox.showerror("Erro", "Localização não encontrada")
        return None
    elif res.status_code != 200:
        messagebox.showerror("Erro", "Falha ao obter dados climáticos")
        return None
    
    weather = res.json()
    try:
        icon_id = weather['weather'][0]['icon']
        temperature = weather['main']['temp'] - 273.15  # Converter de Kelvin para Celsius
        humidity = weather['main']['humidity']
        wind_speed = weather['wind']['speed']
        city = weather['name']
        country = weather['sys']['country']
        pressure = weather['main']['pressure']
    except KeyError as e:
        messagebox.showerror("Erro", f"Dados ausentes na resposta: {e}")
        return None

    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
    return icon_url, temperature, humidity, wind_speed, city, country, pressure


# Função para analisar dados climáticos e identificar padrões anormais e condições propícias para desastres naturais
def analyze_weather_data(temperature, humidity, wind_speed, pressure):
    global previous_temperature, previous_humidity

    anomalies = []

    # Verificar variações abruptas na temperatura
    if previous_temperature is not None:
        if abs(temperature - previous_temperature) > 5:  # Variação maior que 5ºC
            anomalies.append("Mudança abrupta na temperatura detetada!")

    # Verificar mudanças rápidas na humidade
    if previous_humidity is not None:
        if abs(humidity - previous_humidity) > 20:  # Exemplo: variação maior que 20%
            anomalies.append("Mudança abrupta na humidade detetada!")

    # Verificar condições propícias para desastres naturais
    if humidity > 70 and pressure < 1000:
        anomalies.append("Alerta: Condições propícias para inundações!")
    if temperature < 0:
        anomalies.append("Alerta: Condições propícias para neve!")
    if wind_speed is not None and wind_speed > 50:
        anomalies.append("Alerta: Condições propícias para furacões ou tornados!")

    # Atualizar os valores anteriores
    previous_temperature = temperature
    previous_humidity = humidity

    return anomalies


# Função para exibir anomalias em uma nova janela
def show_anomalies():
    if not anomalies:
        messagebox.showinfo("Anomalias", "Nenhuma anomalia detetada.")
        return
    
    # Cria uma nova janela para mostrar as anomalias
    anomalies_window = Toplevel(root)
    anomalies_window.title("Anomalias Detetadas")
    anomalies_window.geometry("350x200")  # Aumentar o tamanho da janela

    # Exibe as anomalias na nova janela
    for anomaly in anomalies:
        anomaly_label = tk.Label(anomalies_window, text=anomaly, font=("Helvetica", 12))
        anomaly_label.pack(pady=5)
    

        # Verificar se é um alerta para desastre natural e exibir uma caixa de diálogo
        if "Alerta" in anomaly:
            messagebox.showwarning("Alerta de Desastre Natural", anomaly)


    # Adiciona um botã para voltar atrás
    close_button = tk.Button(anomalies_window, text="Fechar", command=anomalies_window.destroy)
    close_button.pack(pady=5)


# Função para criar histórico de dados climáticos
def create_history(temperature, humidity, wind_speed, pressure, city, country):
    global previous_temperature, previous_humidity, previous_wind_speed, previous_pressure

    # Cria um dicionário com os dados atuais e um timestamp
    data_entry = {
        'Dia e hora:': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Localização:': f"{city}, {country}",
        'Temperatura': temperature,
        'Humidade': humidity,
        'Velocidade do vento': wind_speed,
        'Pressão': pressure
    }
    
    # Adiciona a entrada ao histórico
    historical_data.append(data_entry)
    
    # Atualiza as variáveis globais
    previous_temperature = temperature
    previous_humidity = humidity
    previous_wind_speed = wind_speed
    previous_pressure = pressure
                              
                              
def access_history():   
    # Cria uma nova janela para mostrar o histórico
    history_window = Toplevel(root)
    history_window.title("Histórico de dados climáticos")
    history_window.geometry("400x600")  # Aumentar o tamanho da janela

    # Exibe o histórico na nova janela
    for entry in historical_data:
        
        entry_text = f"Dia e hora: {entry['Dia e hora:']}\n"
        entry_text += f"Localização: {entry['Localização:']}\n"  
        entry_text += f"Temperatura: {entry['Temperatura']:.1f}ºC\n"
        entry_text += f"Humidade: {entry['Humidade']}%\n"
        entry_text += f"Velocidade do vento: {entry['Velocidade do vento']:.1f} m/s\n"
        entry_text += f"Pressão: {entry['Pressão']:.1f} hPa\n"
        entry_label = tk.Label(history_window, text=entry_text, font=("Helvetica", 12))
        entry_label.pack(pady=5)
     
    # Adiciona um botão para voltar atrás
    close_button = tk.Button(history_window, text="Fechar", command=history_window.destroy)
    close_button.pack(pady=5)

# Função para buscar informações sobre o clima
def search():
    global anomalies
    city = city_entry.get()
    result = get_weather(city)
    if result is None:
        return
    
    icon_url, temperature, humidity, wind_speed, city, country, pressure = result
    location_label.configure(text=f"{city}, {country}")

    image = Image.open(requests.get(icon_url, stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon

    temperature_label.configure(text=f"Temperatura: {temperature:.1f}ºC")
    humidity_label.configure(text=f"Humidade: {humidity:.1f}%")
    windspeed_label.configure(text=f"Velocidade do Vento: {wind_speed:.1f} m/s")
    pressure_label.configure(text=f"Pressão: {pressure:.1f} hPa")

    # Analisar dados climáticos e armazenar anomalias
    anomalies = analyze_weather_data(temperature, humidity, wind_speed, pressure)

    # Atualizar o histórico de dados climáticos
    create_history(temperature, humidity, wind_speed, pressure, city, country)


# Configuração da janela principal
root = ttk.Window(themename="morph")
root.title("Aplicativo de Clima")
root.geometry("500x600")  # Aumentar a altura da janela principal

city_entry = ttk.Entry(root, font="Helvetica, 18")
city_entry.pack(pady=10)

search_button = ttk.Button(root, text="Pesquisar", command=search, bootstyle="Warning")
search_button.pack(pady=10)

location_label = tk.Label(root, font="Helvetica, 25")
location_label.pack(pady=20)

icon_label = tk.Label(root)
icon_label.pack()

temperature_label = tk.Label(root, font="Helvetica, 20")
temperature_label.pack()

humidity_label = tk.Label(root, font="Helvetica, 20")
humidity_label.pack()

windspeed_label = tk.Label(root, font="Helvetica, 20")
windspeed_label.pack()

pressure_label = tk.Label(root, font="Helvetica, 20")
pressure_label.pack()


# Botão para mostrar anomalias
anomalies_button = ttk.Button(root, text="Padrões Anormais", command=show_anomalies, bootstyle="Info")
anomalies_button.pack(pady=20)


# Botão para mostrar histórico
history_button = ttk.Button(root, text="Histórico de Dados Climáticos", command=access_history, bootstyle="Success")
history_button.pack(pady=20)


root.mainloop()
