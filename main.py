import streamlit as st
from whatstk import df_from_whatsapp
import re
import pandas as pd


def remove_emojis_and_tilde(text):
    return re.sub(r'[^\w\s,]', '', text)


st.set_page_config(layout="wide")
st.title('Burpee- und Laufchallenge')
kick = 131
goal = 384

st.markdown(f'## Nächster Kick')
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 30.06.2024 18:00")
with c2:
    st.markdown(f"### Zielpunktezahl: {goal}")
with c3:
    st.markdown(f"### Kickgrenze: {kick}")


df = df_from_whatsapp("_chat.txt")
df['date'] = pd.to_datetime(df['date'])
df = df[df['date'] >= '2024-06-15']
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
df_below_kick = df[df['Punkte'] < kick]
st.divider()
st.markdown(f'## Topsportler')
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"### 1. {df.at[0, 'Sportler']}")
with c2:
    st.markdown(f"### 2. {df.at[1, 'Sportler']}")
with c3:
    st.markdown(f"### 3. {df.at[2, 'Sportler']}")
st.divider()
st.markdown('## Ranking')
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'### Über dem Zielwert von {goal}')
    st.dataframe(df_above_goal)
with c2:
    st.markdown(f'### Über der Kickgrenze von {kick}')
    st.dataframe(df_above_kick)
with c3:
    st.markdown(f'### Unter der Kickgrenze von {kick}')
    st.dataframe(df_below_kick)
