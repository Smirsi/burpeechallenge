import streamlit as st
from whatstk import df_from_whatsapp
import re
import pandas as pd
import numpy as np
from datetime import date
import matplotlib.pyplot as plt


def remove_emojis_and_tilde(text):
    return re.sub(r'[^\w\s,]', '', text)


def plot_soll_kick():
    start_date = pd.to_datetime('2024-06-17')
    end_date = pd.to_datetime('2025-06-16')
    today = pd.to_datetime(date.today())
    total_days = (end_date - start_date).days + 1
    dates = pd.date_range(start=start_date, end=end_date)
    df_plot = pd.DataFrame({'Date': dates})
    df_plot['Soll'] = np.linspace(0, 10000, total_days).astype(int)
    df_plot['Kick'] = (df_plot['Soll'] / 3) * (3 ** (df_plot.index / (total_days - 1)))

    # Plotten von Soll und Kick
    plt.figure(figsize=(12, 6))
    plt.plot(df_plot['Date'], df_plot['Soll'], label='Soll', marker='o')
    plt.plot(df_plot['Date'], df_plot['Kick'], label='Kick', marker='s')

    # Markiere den heutigen Tag mit einem vertikalen Strich
    plt.axvline(x=today, color='r', linestyle='--', linewidth=2, label='Heutiger Tag')

    # Beschriftungen und Titel
    plt.xlabel('Datum')
    plt.ylabel('Punkte')
    plt.title('Verlauf von Soll und Kick')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt


st.set_page_config(page_title='Burpeechallenge', page_icon='burpee.ico', layout="wide")
st.title('Burpee- und Laufchallenge')


# plot = plot_soll_kick()
# st.pyplot(plot.gcf())

plot_goal = True
plot_kick = True
plot_goal_today = True
plot_kick_today = True
plot_kicked = True
color = 'green'

kicked = 131

today = date.today()
days_of_challenge = (today - date(2024, 6, 16)).days
today_goal = 10000 / 365 * days_of_challenge
today_kick = today_goal / (1 + 2 * (date(2025, 6, 16) - today).days / 365)

kick_date = date(2024, 7, 14)
days_of_challenge = (kick_date - date(2024, 6, 16)).days
goal = 10000 / 365 * days_of_challenge
kick = goal / (1 + 2 * (date(2025, 6, 16) - kick_date).days / 365)

st.markdown(f'## Heutiges Ziel')
c1, c2, c3 = st.columns(3)
with c1:
    if today.day < 10:
        if today.month < 10:
            st.markdown(f"### 0{today.day}.0{today.month}.{today.year}")
        else:
            st.markdown(f"### 0{today.day}.{today.month}.{today.year}")
    else:
        if today.month < 10:
            st.markdown(f"### {today.day}.0{today.month}.{today.year}")
        else:
            st.markdown(f"### {today.day}.{today.month}.{today.year}")
with c2:
    st.markdown(f"### Zielpunktezahl: {int(round(today_goal))}")
with c3:
    st.markdown(f"### Kickgrenze: {int(round(today_kick))}")

st.markdown(f'## Nächster Kick')
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 14.07.2024 18:00")
with c2:
    st.markdown(f"### Zielpunktezahl: {int(round(goal))}")
with c3:
    st.markdown(f"### Kickgrenze: {int(round(kick))}")


df = df_from_whatsapp("_chat.txt")
df['date'] = pd.to_datetime(df['date'])
df = df[df['date'] >= '2024-06-15']
# st.dataframe(df)
df['message'] = df['message'].apply(remove_emojis_and_tilde)
df['username'] = df['username'].apply(remove_emojis_and_tilde)
df = df[df['message'].str.isdigit()]
df['message'] = df['message'].astype(int)
df = df.sort_values('date').drop_duplicates('username', keep='last')
df = df.sort_values('message', ascending=False)


df = df.reset_index(drop=True)
df = df.drop(columns=['date'])

df = df.rename(columns={'username': 'Sportler', 'message': 'Punkte'})

df_above_goal = df[df['Punkte'] >= goal]
df_above_kick = df[(df['Punkte'] >= kick) & (df['Punkte'] < goal)]
df_below_kick = df[(df['Punkte'] >= kicked) & (df['Punkte'] < kick)]
df_kicked = df[df['Punkte'] < kicked]
st.divider()
st.markdown(f'## Ranking')
st.markdown(f"### Über dem 2-Wochen-Ziel")
for i in range(len(df['Punkte'])):
    if df.at[i, 'Punkte'] < goal and plot_goal:
        plot_goal = False
        color = 'blue'
        c1, c2, _, c3 = st.columns([3, 3, 1, 1])
        with c1:
            st.markdown(f"### Über dem heutigen Ziel")
    elif df.at[i, 'Punkte'] < today_goal and plot_goal_today:
        plot_goal_today = False
        c1, c2, _, c3 = st.columns([3, 3, 1, 1])
        color = 'blue'
        with c1:
            st.markdown(f"### Über der 2-Wochen-Kickgrenze")
    elif df.at[i, 'Punkte'] < kick and plot_kick:
        plot_kick = False
        c1, c2, _, c3 = st.columns([3, 3, 1, 1])
        color = 'orange'
        with c1:
            st.markdown(f"### Über der heutigen Kickgrenze")
    elif df.at[i, 'Punkte'] < today_kick and plot_kick_today:
        plot_kick_today = False
        c1, c2, _, c3 = st.columns([3, 3, 1, 1])
        color = 'orange'
        with c1:
            st.markdown(f"### Unter der heutigen Kickgrenze")
    elif df.at[i, 'Punkte'] < kicked and plot_kicked:
        plot_kicked = False
        color = 'red'
        c1, c2, _, c3 = st.columns([3, 3, 1, 1])
        with c1:
            st.markdown(f"### Gekickt")
    #  c1, c2, _, c3 = st.columns([3, 3, 1, 1])
    c1, c3 = st.columns([3, 1])
    with c1:
        st.markdown(f"#### :{color}[{i+1}. {df.at[i, 'Sportler']}]")
    # with c2:
    #    st.progress(float(int(df.at[i, 'Punkte']) / int(df.at[0, 'Punkte'])))  # , text=str(df.at[0, 'Punkte']))
    with c3:
        st.markdown(f"### :{color}[{df.at[i, 'Punkte']}]")

# st.divider()
# st.markdown('## Ranking')
# c1, c2, c3, c4 = st.columns(4)
# with c1:
#     st.markdown(f'### Über dem Zielwert von {goal}')
#     st.dataframe(df_above_goal)
# with c2:
#     st.markdown(f'### Über der Kickgrenze von {kick}')
#     st.dataframe(df_above_kick)
# with c3:
#     st.markdown(f'### Unter der Kickgrenze von {kick}')
#     st.dataframe(df_below_kick)
# with c4:
#     st.markdown(f'### Ausgeschieden')
#     st.dataframe(df_kicked)

st.divider()
st.markdown('Daten von 08.07.2024 18:54')

