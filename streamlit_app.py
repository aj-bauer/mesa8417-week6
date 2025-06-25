import streamlit as st
import pandas as pd
import math
from pathlib import Path
import altair as alt

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Montreal Airbnb Data',
    page_icon=':houses:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_bnb_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/listings.csv.gz'
    bnb_df = pd.read_csv(DATA_FILENAME)

    return bnb_df

bnb_df = get_bnb_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
st.title("Exploring Montreal Airbnb Data")
st.markdown('''
Exploration of the Inside Airbnb dataset (see more: https://insideairbnb.com/montreal/).
            
By Avi Bauer for MESA8417, Summer 2025.''')

with st.sidebar:

    st.header("Filters")
    
    # Choose neighborhood (dropdown)
    neighborhood = st.selectbox(
        label="Neighborhood",
        options=["Montreal"] + list(bnb_df["neighbourhood_cleansed"].unique())
    )

    # Filter by min/max rating
    rating_range = st.slider(label="Overall Rating",
                                 min_value=float(bnb_df["review_scores_rating"].min()), 
                                 max_value=float(bnb_df["review_scores_rating"].max()), 
                                 value=(0.0, 5.0))

# Apply filters
bnb_filtered = bnb_df if neighborhood == "Montreal" else bnb_df[bnb_df["neighbourhood_cleansed"] == neighborhood]
bnb_filtered = bnb_filtered[bnb_filtered["review_scores_rating"].between(*rating_range)]


# Make a map of Montreal
st.header(f"WHERE are the Airbnb listings in {neighborhood}?")
st.metric(label="Listings",value="")
st.map(data=bnb_filtered, 
       latitude="latitude", 
       longitude="longitude",
       size=20)

# 