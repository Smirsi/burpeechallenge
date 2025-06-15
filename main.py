import streamlit as st
import re
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objs as go


def remove_emojis_and_tilde(text):
    return re.sub(r'[^\w\s,]', '', text)


def df_from_whatsapp(filename):
    """Parst einen WhatsApp-Chat aus einer Textdatei in ein DataFrame."""
    import re
    import pandas as pd

    pattern = r'\[(.*?)\] (.*?): (.*)'
    messages = []

    with open(filename, encoding='utf-8') as f:
        for line in f:
            match = re.match(pattern, line)
            if match:
                datetime_str, sender, message = match.groups()
                messages.append([datetime_str, sender, message])

    df_whatsapp = pd.DataFrame(messages, columns=['date', 'username', 'message'])
    return df_whatsapp


st.set_page_config(page_title='Triple-Everest', page_icon='everest.ico', layout="wide")
st.title('Triple-Everest Challenge')

plot_done = True
plot_goal = True
plot_kick = True
plot_goal_today = True
plot_kick_today = True
plot_kicked = True
color = 'violet'

date_start = date(2024, 6, 16)
date_end = date_start + timedelta(days=365)
date_today = date.today()
days_of_challenge = (date_today - date_start).days
total_points_goal = 10000

kick_date = date_start + timedelta(days=14)
while kick_date < date_today:
    kick_date += timedelta(days=14)
days_of_challenge = (kick_date - date_start).days
points_goal_next = total_points_goal / 365 * days_of_challenge
points_kick_next = points_goal_next / (1 + 2 * (date_end - kick_date).days / 365)
points_kicked = points_goal_next / (1 + 2 * (date_end - kick_date + timedelta(days=14)).days / 365)

st.subheader(f'Nächster Kick')
c1, c2, c3 = st.columns(3)
with c1:
    if kick_date.day < 10:
        if kick_date.month < 10:
            st.markdown(f"#### 0{kick_date.day}.0{kick_date.month}.{kick_date.year} 18:00")
        else:
            st.markdown(f"#### 0{kick_date.day}.{kick_date.month}.{kick_date.year} 18:00")
    else:
        if kick_date.month < 10:
            st.markdown(f"#### {kick_date.day}.0{kick_date.month}.{kick_date.year} 18:00")
        else:
            st.markdown(f"#### {kick_date.day}.{kick_date.month}.{kick_date.year} 18:00")
with c2:
    st.markdown(f"#### Zielpunktezahl: {int(round(points_goal_next))}")
with c3:
    st.markdown(f"#### Kickgrenze: {int(round(points_kick_next))}")
st.divider()

# Get DATA
df = df_from_whatsapp("_chat.txt")
df['date'] = pd.to_datetime(df['date'])
df = df[df['date'] >= '2024-06-15']
df['message'] = df['message'].apply(remove_emojis_and_tilde)
df['username'] = df['username'].apply(remove_emojis_and_tilde)
df['username'] = df['username'].str.strip()
df = df[df['message'].str.isdigit()]
df['message'] = df['message'].astype(int)
df = df[df['message'] <= 11000]
df = df.rename(columns={'username': 'Sportler', 'message': 'Punkte', 'date': 'Datum'})

# Frauds
df = df[df['Sportler'] != 'Reini Puhringer']
df = df[df['Sportler'] != 'Mario Wiesinger']  # 145
df = df.reset_index(drop=True)

# Top 10 User bestimmen
topX_number = 10
final_punkte = df.sort_values(['Sportler', 'Datum']).groupby('Sportler').tail(1)
topX = final_punkte.sort_values('Punkte', ascending=False).head(topX_number)['Sportler'].tolist()
top_df = df[df['Sportler'].isin(topX)]

st.subheader(f'Punkteverlauf der Top 10')
# Plotly-Diagramm
fig = go.Figure()
for user, group in top_df.groupby('Sportler'):
    group = group.sort_values('Datum')
    fig.add_trace(go.Scatter(x=group['Datum'], y=group['Punkte'],
                             mode='lines+markers',
                             name=user))

fig.update_layout(xaxis_title='Datum',
                  yaxis_title='Punkte',
                  hovermode='x unified')

st.plotly_chart(fig, use_container_width=True)

# Write all personen down in a list
df = df.sort_values('Datum').drop_duplicates('Sportler', keep='last')
df = df.sort_values('Punkte', ascending=False)
df = df.reset_index(drop=True)
df = df.drop(columns=['Datum'])

st.divider()
st.subheader(f'Ranking')
c = st.columns(5)
ci = 0
c[ci].markdown(f"#### Challenge Completed")
for i in range(len(df['Punkte'])):
    if df.at[i, 'Punkte'] < 10000 and plot_done:
        plot_done = False
        color = 'green'
        c[1].markdown(f"#### Über dem 2-Wochen-Ziel")
        ci = 1
    if df.at[i, 'Punkte'] < points_goal_next and plot_goal:
        plot_goal = False
        color = 'blue'
        c[2].markdown(f"#### Über der 2-Wochen-Kickgrenze")
        ci = 2
    if df.at[i, 'Punkte'] < points_kick_next and plot_kick:
        plot_kick = False
        color = 'orange'
        c[3].markdown(f"#### Unter der 2-Wochen-Kickgrenze")
        ci = 3
    if df.at[i, 'Punkte'] < points_kicked and plot_kick_today:
        plot_kick_today = False
        color = 'red'
        c[4].markdown(f"#### Gekickt")
        ci = 4

    print(df.at[i, 'Sportler'])
    # Double winners (2024, 2025)
    if df.at[i, 'Sportler'] in ['Valentin Eder', 'Philip']:
        df.at[i, 'Sportler'] = df.at[i, 'Sportler'] + ' 🥇🥇'
    # Winners 2024
    if df.at[i, 'Sportler'] in ['Norbert Gattringer', 'Tamara Hofer', 'Christoph Hofer']:
        df.at[i, 'Sportler'] = df.at[i, 'Sportler'] + ' 🥇'
    # Winners 2025
    if df.at[i, 'Sportler'] in ['Carina Gstottner', 'Franzi', 'Mathias', 'Paul Schmidt', 'Simon Paireder', 'Eva']:
        df.at[i, 'Sportler'] = df.at[i, 'Sportler'] + ' 🥇'
    c[ci].markdown(f"##### :{color}[{i + 1}. | {df.at[i, 'Punkte']} | {df.at[i, 'Sportler']}]")

st.divider()
st.markdown('Daten von 15.06.2025 10:09')
