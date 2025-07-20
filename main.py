import streamlit as st
from whatstk import df_from_whatsapp
import re
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objs as go
import os


# 1. Authentifizierung für Google Drive
# @st.cache_resource
# def authenticate_drive():
#     gauth = GoogleAuth()
#     gauth.LocalWebserverAuth()  # Nur beim ersten Mal notwendig
#     return GoogleDrive(gauth)
#
# drive = authenticate_drive()


# @st.dialog('Daten updaten')
# def update_data_file(path):
#     # save_path = os.path.join(os.getcwd(), "_chat.txt")  # oder ein anderer Pfad
#     # save_path = "_chat.txt"
#     file = st.file_uploader('Datei auswählen', type=['.zip'], accept_multiple_files=False)
#     pw = st.text_input('Passwort')
#     if st.button("File hochladen", type="primary", use_container_width=True) and pw == "Hogi" and file is not None:
#         with open(path, "wb") as f:
#             f.write(file.getbuffer())
#         st.rerun()
        
    
def remove_emojis_and_tilde(text):
    return re.sub(r'[^\w\s,]', '', text)


def extract_points(text):
    """
    Extrahiert Punkte aus einer WhatsApp-Nachricht.
    Zählt sowohl einfache Zahlen (auch mit . oder Leerzeichen) als auch Kombinationen wie '182hm 13klimmzüge'.
    """
    text = text.lower()
    text = text.replace(".", "").replace(" ", "")  # Tausendertrennung entfernen
    total = 0

    # Suche nach Höhenmetern (z. B. "182hm", "182hm", "182hm")
    matches_hm = re.findall(r'(\d+)\s*hm', text)
    total += sum(int(hm) for hm in matches_hm)

    # Suche nach Klimmzügen (z. B. "13klimmzüge", "13klimmes")
    matches_klimm = re.findall(r'(\d+)\s*(klimmzüge|klimmes|klimmzug)', text)
    total += sum(int(klimm) * 1 for klimm, _ in matches_klimm)  # ggf. Gewichtung anpassen

    # Falls der Text nur aus einer Zahl besteht (nach Punkt-/Leerzeichen-Entfernung), zähle diese auch
    if total == 0 and re.fullmatch(r'\d+', text):
        total = int(text)

    return total if total <= 270000 else 0  # Obergrenze


def rules():
    st.markdown("""
    #### 🏔 Ziel  
    Innerhalb von **einem Jahr** (23.06.2025–22.06.2026) **müssen 26.547 Punkte** gesammelt werden.  

    ---

    #### 🌟 Was zählt als Punkte?

    ✅ **Höhenmeter** (egal, welchen Sport du ausübst — jedoch muss dieser **unmotorisiert** sein, außerdem zählen 
    nur **positive** Höhenmeter (nach oben)).  
    ➥ 1 positiver Höhenmeter = 1 Punkt  

    ✅ **Klimmzüge:**  
    ➥ Männer: 1 Klimmzug = 1 Punkt  
    ➥ Frauen: 1 Klimmzug = 3 Punkte (ein Widerstandsband darf bei Bedarf verwendet werden)

    ---

    #### ⏱ Kickgrenze

    ✅ Alle 2 Wochen (Sonntag 18:00) werden Personen gekickt, die unter der jeweils aktuellen Kickgrenze liegen.  

    ✅ Die **Zielgrenze** wächst **linear** von 0 auf 26.547 im Laufe eines Jahres.  

    ✅ Die **Kickgrenze** ist **nichtlinear**:
    
    $Kickgrenze = \dfrac{Zielgrenze}{1 + 2 * \dfrac{(Enddatum - Kickdatum)}{365}}$

    ---

    🚀 Sei dabei, gib Gas und erreiche den Gipfel!  
    """)


st.set_page_config(page_title='Triple-Everest', page_icon='everest.ico', layout="wide")
st.title('🏔 Triple-Everest Challenge 🏔')

with st.expander("Regeln", expanded=False):
    rules()

plot_done = True
plot_goal = True
plot_today = True
plot_kick = True
plot_goal_today = True
plot_kick_today = True
plot_kicked = True
color = 'violet'

date_start = date(2025, 6, 22)
date_end = date_start + timedelta(days=365)
date_today = date.today()
days_of_challenge = (date_today - date_start).days
total_points_goal = 26547

kick_date = date_start + timedelta(days=14)
while kick_date < date_today:
    kick_date += timedelta(days=14)
days_of_challenge = (kick_date - date_start).days
points_goal_next = total_points_goal / 365 * days_of_challenge
points_goal_today = total_points_goal / 365 * (date_today - date_start).days
points_kick_next = points_goal_next / (1 + 2 * (date_end - kick_date).days / 365)

points_kicked = (total_points_goal / 365 * (days_of_challenge - 15)) / (1 + 2 * (date_end - kick_date).days / 365)

st.subheader(f'Nächster Kick')
c1, c2, c3, c4 = st.columns(4)
if kick_date.day < 10:
    if kick_date.month < 10:
        c1.markdown(f"#### 0{kick_date.day}.0{kick_date.month}.{kick_date.year} 18:00")
    else:
        c1.markdown(f"#### 0{kick_date.day}.{kick_date.month}.{kick_date.year} 18:00")
else:
    if kick_date.month < 10:
        c1.markdown(f"#### {kick_date.day}.0{kick_date.month}.{kick_date.year} 18:00")
    else:
        c1.markdown(f"#### {kick_date.day}.{kick_date.month}.{kick_date.year} 18:00")
c2.markdown(f"#### Zielpunktezahl: {int(round(points_goal_next))}")
c3.markdown(f"#### Kickgrenze: {int(round(points_kick_next))}")
c4.markdown(f"#### Heutiges Ziel: {int(round(points_goal_today))}")
st.divider()

# # Get DATA
# # Ordner für TXT-Dateien
# profiles_dir = './'
# # if not os.path.exists(profiles_dir):
# #    os.makedirs(profiles_dir)
#
# file_path = os.path.join(profiles_dir, "_chat.txt")

df = df_from_whatsapp("_chat.txt")
df['date'] = pd.to_datetime(df['date'])
df = df[df['date'] >= '2025-06-23']
df['message'] = df['message'].apply(remove_emojis_and_tilde)
df['username'] = df['username'].apply(remove_emojis_and_tilde)
df['username'] = df['username'].str.strip()

df['Punkte'] = df['message'].apply(extract_points)
df = df[df['Punkte'] > 0]

# df = df[df['message'].str.isdigit()]
# df['message'] = df['message'].astype(int)
# df = df[df['message'] <= 27000]
# st.dataframe(df)
df = df.rename(columns={'username': 'Sportler', 'date': 'Datum'})
# df = df.rename(columns={'username': 'Sportler', 'message': 'Punkte', 'date': 'Datum'})

# Frauds
# df = df[df['Sportler'] != 'Reini Puhringer']
# df = df[df['Sportler'] != 'Mario Wiesinger']  # 145
# df = df.reset_index(drop=True)

# # Nachrichten aus SQLite holen
# conn = sqlite3.connect('messages.sqlite')
# df_wa = pd.read_sql('SELECT * FROM messages', conn)
# conn.close()
#
# # Filtern, damit nur Nachrichten, die aus einer Zahl bestehen, drin sind
# df_wa = df_wa.copy()
# df_wa['message'] = df_wa['message'].str.strip()
# df_wa = df_wa[df_wa['message'].str.isdigit()]
# df_wa['message'] = df_wa['message'].astype(int)
#
# # Spalten passend machen
# df_wa = df_wa.copy()
# df_wa = df_wa.rename(columns={'sender': 'Sportler', 'message': 'Punkte', 'timestamp': 'Datum'})
# df_wa['Datum'] = pd.to_datetime(df_wa['Datum'])
#
# # vorhandenen Datensatz mit WhatsApp-Datensatz zusammenfügen
# df = pd.concat([df_file[['Sportler', 'Punkte', 'Datum']],
#                 df_wa[['Sportler', 'Punkte', 'Datum']]],
#                ignore_index=True)

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
# st.dataframe(df.sort_values('Sportler', ascending=False))
st.divider()
st.subheader(f'Ranking')
c = st.columns(6)
ci = 0
c[ci].markdown(f"#### Challenge Completed")
for i in range(len(df['Punkte'])):
    if df.at[i, 'Punkte'] < total_points_goal and plot_done:
        plot_done = False
        color = 'green'
        c[1].markdown(f"#### Über dem 2-Wochen-Ziel")
        ci = 1
    if df.at[i, 'Punkte'] < points_goal_next and plot_goal:
        plot_goal = False
        color = 'blue'
        c[2].markdown(f"#### Über dem heutigen Ziel")
        ci = 2
    if df.at[i, 'Punkte'] < points_goal_today and plot_today:
        plot_today = False
        color = 'orange'
        c[3].markdown(f"#### Über der 2-Wochen-Kickgrenze")
        ci = 3
    if df.at[i, 'Punkte'] < points_kick_next and plot_kick:
        plot_kick = False
        color = 'grey'
        c[4].markdown(f"#### Unter der 2-Wochen-Kickgrenze")
        ci = 4
    if df.at[i, 'Punkte'] < points_kicked and plot_kick_today:
        plot_kick_today = False
        color = 'red'
        c[5].markdown(f"#### Gekickt")
        ci = 5

    # Double winners (2024, 2025)
    if df.at[i, 'Sportler'] in ['Valentin Eder', 'Philip']:
        df.at[i, 'Sportler'] = df.at[i, 'Sportler'] + ' 🏆🏆'
    # Winners 2024
    if df.at[i, 'Sportler'] in ['Norbert Gattringer', 'Tamara Hofer', 'Christoph Hofer']:
        df.at[i, 'Sportler'] = df.at[i, 'Sportler'] + ' 🏆'
    # Winners 2025
    if df.at[i, 'Sportler'] in ['Carina Gstottner', 'Franzi', 'Mathias', 'Paul Schmidt', 'Simon Paireder', 'Eva']:
        df.at[i, 'Sportler'] = df.at[i, 'Sportler'] + ' 🏆'
    c[ci].markdown(f"##### :{color}[{i + 1}. | {df.at[i, 'Punkte']} | {df.at[i, 'Sportler']}]")

st.divider()
c1, c2 = st.columns(2)
c1.markdown('Daten von 20.07.2025 18:44')
# if st.button('Daten updaten', type="primary", use_container_width=True):
#    update_data_file(file_path)
