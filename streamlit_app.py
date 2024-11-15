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
    
    fig = plt.figure(figsize=(None, 6))
    
    plt.pie(avg_quantities, labels=statuses, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Average Quantity by Order Status', fontsize=14)
    st.pyplot(fig)

def query_orders_by_shipping():
    curs.execute('''
    SELECT 
        SHIPPING, 
        COUNT(ORDERID) AS total_orders, 
        SUM(QUANTITY) AS total_quantity,
        SUM(TOTAL_PRICE) AS total_sales
    FROM 
        book_orders
    GROUP BY 
        SHIPPING;
    ''')
        # ดึงข้อมูลจากผลลัพธ์คิวรี่
    tables = [row for row in curs.fetchall()]
    shipping_methods = [row[0] for row in tables]
    total_orders = [row[1] for row in tables]
    total_quantity = [row[2] for row in tables]
    total_sales = [row[3] for row in tables]
    # กำหนดสีให้กับ Shipping Method
    colors = ['skyblue' if shipping == 'Standard' else 'salmon' for shipping in shipping_methods]

    # สร้างกราฟหลายๆ กราฟ
    
    fig, ax = plt.subplots(1, 3, figsize=(None, 6))

    # กราฟแสดงจำนวนคำสั่งซื้อ
    ax[0].bar(shipping_methods, total_orders, color=colors)
    ax[0].set_title('Total Orders by Shipping')
    ax[0].set_xlabel('Shipping Method')
    ax[0].set_ylabel('Total Orders')

    # กราฟแสดงปริมาณรวม
    ax[1].bar(shipping_methods, total_quantity, color=colors)
    ax[1].set_title('Total Quantity by Shipping')
    ax[1].set_xlabel('Shipping Method')
    ax[1].set_ylabel('Total Quantity')

    # กราฟแสดงยอดขายรวม
    ax[2].bar(shipping_methods, total_sales, color=colors)
    ax[2].set_title('Total Sales by Shipping')
    ax[2].set_xlabel('Shipping Method')
    ax[2].set_ylabel('Total Sales')

    # ปรับแต่งพื้นที่ระหว่างกราฟ
    plt.tight_layout()

    # แสดงกราฟใน Streamlit
    st.pyplot(fig)

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
    page_ids = [str(row[0]) for row in tables]  # Convert IDs to strings
    view_counts = [row[1] for row in tables]

    # ตรวจสอบข้อมูลก่อนวาดกราฟ
    if not page_ids or not view_counts:
        st.error("No data available to display.")
        return

    # สร้างกราฟด้วย Plotly
    fig = px.bar(
        x=view_counts,
        y=page_ids,
        orientation='h',
        title='Top 10 Most Viewed Pages (Horizontal Bar Chart)',
        labels={'x': 'View Counts', 'y': 'Page IDs'},
        color_discrete_sequence=['#483D8B'] * len(view_counts)  # สี Light Sea Green
    )
    fig.update_layout(
        xaxis_title="View Counts",
        yaxis_title="Page IDs",
        yaxis=dict(categoryorder='total ascending'),
        title_font_size=16
    )


    # แสดงกราฟใน Streamlit
    st.plotly_chart(fig)
    

def query_user_count_by_gender_region2():
    # ดึงข้อมูลจากฐานข้อมูล
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
    
    # สร้าง dictionary สำหรับเก็บจำนวนผู้ใช้
    counts = {region: {gender: 0 for gender in gender_labels} for region in regions}
    
    # เติมข้อมูลใน counts dictionary
    for gender, region, count in tables:
        counts[region][gender] += count

    bar_width = 0.25  # กำหนดความกว้างของบาร์ในแต่ละกลุ่ม
    ind = range(len(regions))

    # กำหนดสีสำหรับแต่ละเพศ
    gender_colors = {
        'FEMALE': '#87CEFA',  # Light Sky Blue
        'MALE': '#F08080',    # Light Coral
        'OTHER': '#BA55D3'    # Medium Orchid
    }
    
    fig, ax = plt.subplots(figsize=(None, 6))
    for i, gender in enumerate(gender_labels):
        ax.bar(
            [x + (i - 1) * bar_width for x in ind],  # ปรับตำแหน่งบาร์
            [counts[region][gender] for region in regions],
            bar_width,
            label=gender,
            color=gender_colors.get(gender, 'gray')
        )
    
    ax.set_title('User Count by Gender and Region', fontsize=14)
    ax.set_xlabel('Region', fontsize=12)
    ax.set_ylabel('User Count', fontsize=12)
    ax.set_xticks([x for x in ind])
    ax.set_xticklabels(regions, rotation=45)
    ax.legend(title='Gender')
    
    # แสดงกราฟ
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

    # Find the max revenue
    max_revenue = max(revenues)

    # Create a color list where the max value gets 'orangered' and others get 'skyblue'
    colors = ['orangered' if revenue == max_revenue else 'skyblue' for revenue in revenues]

    fig = plt.figure(figsize=(None, 6))
    plt.bar(genres, revenues, color=colors)
    plt.title('Total Revenue by Genre', fontsize=14)
    plt.xlabel('Genre', fontsize=12)
    plt.ylabel('Total Revenue (USD)', fontsize=12)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)


# Function for Top 10 Users by Order Count (horizontal bar chart with Plotly)
def query_top_users_by_order_count():
    curs.execute(''' 
    SELECT 
        USERID, 
        COUNT(ORDERID) AS order_count 
    FROM 
        book_orders
    GROUP BY 
        USERID
    ORDER BY 
        order_count DESC
    LIMIT 5;
    ''')
    tables = [row for row in curs.fetchall()]
    user_ids = [row[0] for row in tables]
    order_counts = [row[1] for row in tables]

    # Find the max order_count
    max_order_count = max(order_counts)

    # Create a color list where the maximum value gets 'orangered' and the others 'skyblue'
    colors = ['orangered' if count == max_order_count else 'skyblue' for count in order_counts]

    # Create a horizontal bar chart with Plotly
    fig = px.bar(
        x=order_counts,
        y=user_ids,
        orientation='h',
        labels={'x': 'Order Count', 'y': 'User ID'},
        title='Top 5 Users by Order Count',
        color=colors,  # Use custom colors
        color_discrete_map={'orangered': 'orangered', 'skyblue': 'skyblue'},  # Map colors to specific values
    )
    st.plotly_chart(fig, use_container_width=True)

# Set up Streamlit layout with 1 row per graph
st.title('Bookshop Omakase - Data Analysis')

# Create a 1x1 layout for each chart
col1, col2 = st.columns(2)

with col1:
    query_avg_quantity()
    query_orders_by_shipping()

with col2:
    query_top_pages()
    query_total_revenue_by_genre()

# Display user count by gender and region chart
query_user_count_by_gender_region2()

# Additional chart for Top 5 Users by Order Count
query_top_users_by_order_count()
