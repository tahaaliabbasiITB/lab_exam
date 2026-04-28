import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Warehouse management system", layout="wide")

BACKEND_URL = "https://ominous-chainsaw-qvqqpg4j45w526g97-3000.app.github.dev/items"

st.title("Warehouse management system")

@st.cache_data(ttl=60) 
def get_data():
    try:
        response = requests.get(BACKEND_URL)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return pd.DataFrame()

df = get_data()

if not df.empty:
    search_query = st.text_input("Search by Name or Location", "")

    if search_query:
        filtered_dataframe = df[
            df['name'].str.contains(search_query, case=False, na=False) |
            df['location'].str.contains(search_query, case=False, na=False)
        ]
    else:
        filtered_dataframe = df

    
    st.write(f"Showing {len(filtered_dataframe)} items")
    
    st.dataframe(filtered_dataframe, use_container_width=True, hide_index=True)

else:
    st.warning("No data found or backend is offline.")