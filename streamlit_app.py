import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pinotdb import connect
import plotly.express as px
from datetime import datetime

# Connect to the Pinot database
conn = connect(host='13.214.194.35', port=8099, path='/query/sql', schema='http')
curs = conn.cursor()

# Function to create and display a pie chart for average quantity by status
def query_avg_quantity():
    curs.execute(''' 
    SELECT 
        STATUS, 
        AVG(QUANTITY) AS avg_quantity 
    FROM 
        book_orders
    GROUP BY 
        STATUS;
    ''')
    tables = [row for row in curs.fetchall()]
    statuses = [row[0] for row in tables]
    avg_quantities = [row[1] for row in tables]
    
    plt.figure(figsize=(8, 8))
    plt.pie(avg_quantities, labels=statuses, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Average Quantity by Order Status', fontsize=14)
    st.pyplot(plt)

# Function to create and display a pie chart for top 10 most viewed pages
def query_top_pages():
    curs.execute(''' 
    SELECT 
        pageid, 
        COUNT(*) AS view_count 
    FROM 
        1_pageviews
    GROUP BY 
        pageid
    ORDER BY 
        view_count DESC
    LIMIT 10;
    ''')
    tables = [row for row in curs.fetchall()]
    page_ids = [row[0] for row in tables]
    view_counts = [row[1] for row in tables]
    
    plt.figure(figsize=(8, 8))
    plt.pie(view_counts, labels=page_ids, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Top 10 Most Viewed Pages', fontsize=14)
    st.pyplot(plt)

# Function to create and display a stacked bar chart for user count by gender and region
def query_user_count_by_gender_region():
    curs.execute(''' 
    SELECT 
        gender,
        regionid,
        COUNT(*) AS user_count
    FROM 
        2_users
    GROUP BY 
        gender, regionid
    ORDER BY 
        user_count DESC;
    ''')
    tables = [row for row in curs.fetchall()]
    regions = sorted(set([row[1] for row in tables]))
    gender_labels = sorted(set([row[0] for row in tables]))
    counts = {region: {gender: 0 for gender in gender_labels} for region in regions}
    
    for gender, region, count in tables:
        counts[region][gender] += count

    bar_width = 0.5
    ind = range(len(regions))

    fig, ax = plt.subplots(figsize=(10, 6))
    bottoms = [0] * len(regions)
    for gender in gender_labels:
        ax.bar(ind, [counts[region][gender] for region in regions], bar_width, label=gender, bottom=bottoms)
        bottoms = [bottoms[i] + counts[regions[i]][gender] for i in range(len(regions))]
    
    ax.set_title('User Count by Gender and Region', fontsize=14)
    ax.set_xlabel('Region', fontsize=12)
    ax.set_ylabel('User Count', fontsize=12)
    ax.set_xticks(ind)
    ax.set_xticklabels(regions, rotation=45)
    ax.legend(title='Gender')
    st.pyplot(fig)

# Function to create and display a bar chart for total revenue by genre
def query_total_revenue_by_genre():
    curs.execute(''' 
    SELECT 
        GENRE, 
        SUM(TOTAL_PRICE) AS total_revenue 
    FROM 
        book_orders
    GROUP BY 
        GENRE
    ORDER BY 
        total_revenue DESC;
    ''')
    tables = [row for row in curs.fetchall()]
    tables = [(genre if genre is not None else "Others", revenue) for genre, revenue in tables]
    genres = [row[0] for row in tables]
    revenues = [row[1] for row in tables]
    
    plt.figure(figsize=(10, 6))
    plt.bar(genres, revenues, color='blue')
    plt.title('Total Revenue by Genre', fontsize=14)
    plt.xlabel('Genre', fontsize=12)
    plt.ylabel('Total Revenue (USD)', fontsize=12)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(plt)

# Set up Streamlit layout with 2 rows and 2 columns
st.title('Data Analysis with Pinot and Matplotlib')

# Create a 2x2 layout using columns
col1, col2 = st.columns(2)

# Query and display charts in the first row
with col1:
    query_avg_quantity()
with col2:
    query_top_pages()

# Query and display charts in the second row
with col1:
    query_user_count_by_gender_region()
with col2:
    query_total_revenue_by_genre()
