import streamlit as st
from whatstk import WhatsAppChat, df_from_whatsapp
from whatstk.data import whatsapp_urls

st.set_page_config(layout="wide")
st.title('Burpee- und Laufchallenge')

df = df_from_whatsapp("path/to/_chat.txt")
st.dataframe(df)
