import streamlit as st
import pandas as pd
import math
from pathlib import Path
import altair as alt

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Montreal Airbnb Data',
    page_icon=':houses:', # This is an emoji shortcode. Could be a URL too.
    layout="wide"
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
    
    # make price a float
    bnb_df["price_float"] = bnb_df["price"].str.replace(r'[^\d.]', '', regex=True).astype(float)

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

    st.header("Narrow it down!")
    
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
    
    # Filter by price
    price_max = st.number_input(label="Max Price",
                                min_value=0.00,
                                max_value=None,
                                value=800.00,
                                step=50.00)

# Apply data filters
bnb_filtered = bnb_df if neighborhood == "Montreal" else bnb_df[bnb_df["neighbourhood_cleansed"] == neighborhood]
bnb_filtered = bnb_filtered[bnb_filtered["review_scores_rating"].between(*rating_range)]
bnb_filtered = bnb_filtered[bnb_filtered["price_float"] <= price_max]

# Make a map of Montreal
st.header(f"WHERE are the Airbnb listings in {neighborhood}?")
st.markdown(f"There are {len(bnb_filtered)} listings in {neighborhood} at or below ${price_max:.0f} with a rating between {rating_range[0]} and {rating_range[1]}. Wow!")

st.map(data=bnb_filtered, 
    latitude="latitude", 
    longitude="longitude",
    size=20)

# This is the only way I can figure how to add space...
st.markdown(" ")
st.markdown(" ")

# define columns
col1, col2 = st.columns(spec=2, gap="medium")

# Make a pie chart of types of listings
with col1:

    select_slice = alt.selection_point(name="roomtype", fields=['room_type'], bind="legend", resolve="global")

    room_types = alt.Chart(bnb_filtered).mark_arc(innerRadius=20, stroke="#fff").encode(
        alt.Theta("count(room_type):Q", sort="descending").stack(True),
        alt.Radius("count(room_type)").scale(type="sqrt", zero=True, rangeMin=10),
        color=alt.Color("room_type:N").title("Room Type"),
        opacity=alt.when(select_slice).then(alt.value(1)).otherwise(alt.value(0.2)),
        tooltip=[alt.Tooltip("room_type",title="Type"),
            alt.Tooltip("count(room_type):Q",title="Count")]
    ).add_params(
        select_slice
    )

    st.header(f"WHAT KINDS of rooms are available in {neighborhood}?")
    # st.markdown(f"Remember, all displayed rooms have ratings between {rating_range[0]} and {rating_range[1]}, and are at/below ${price_max:.0f}. Click the legend to filter prices further by room type.")

    slicer = st.altair_chart(room_types, on_select="rerun")
    
    # filter data by roomtype
    if len(slicer["selection"]["roomtype"]) > 0:
        # st.markdown("Yeah!!")
        rooms = slicer["selection"]["roomtype"][0]["room_type"]
        bnb_filtered = bnb_filtered[bnb_filtered["room_type"] == rooms]
        room_name = rooms
    else:
        room_name = "Airbnb"
    
    # st.markdown(slicer["selection"]["roomtype"])

    
    
# Make a boxplot of prices by accomodates
with col2:

    price_chart = alt.Chart(bnb_filtered).mark_boxplot().encode(
        x=alt.X("price_float:Q", title="Price per Night ($USD)"),
        y=alt.Y("accommodates:N", title="Accomodates", sort="descending"),
        # color=alt.ColorValue("red")
    )
   
    st.header(f"HOW MUCH does a {room_name} cost in {neighborhood}?")
    st.markdown(f"Click the pie chart legend (right) to filter by room type.")

    st.altair_chart(price_chart)
