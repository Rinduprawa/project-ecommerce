import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_order_items_df(df):
    sum_order_item_df = df.groupby("product_category_name_english").order_id.nunique().reset_index().sort_values(by="order_id", ascending=False)
    sum_order_item_df = sum_order_item_df.rename(columns={'product_category_name_english': 'category', 'order_id': 'product_count'})
    return sum_order_item_df

def create_cust_bycity_df(df):
    cust_bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    cust_bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return cust_bycity_df

def create_cust_bystate_df(df):
    cust_bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    cust_bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    cust_bystate_df.head(10)
    return cust_bystate_df

def create_seller_bycity_df(df):
    seller_bycity_df = df.groupby(by="seller_city").seller_id.nunique().reset_index()
    seller_bycity_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    return seller_bycity_df

def create_seller_bystate_df(df):
    seller_bystate_df = df.groupby(by="seller_state").seller_id.nunique().reset_index()
    seller_bystate_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    return seller_bystate_df

def create_highest_rating_df(df):
    score5 = df[df['review_score'] == 5]
    highest_df = score5.groupby(by='product_category_name_english').product_id.nunique().reset_index()
    highest_df.rename(columns={'product_category_name_english': 'category', 'product_id': 'five_star'}, inplace=True)
    return highest_df

def create_lowest_rating_df(df):
    score1 = df[df['review_score'] == 1]
    lowest_df = score1.groupby(by='product_category_name_english').product_id.nunique().reset_index()
    lowest_df.rename(columns={'product_category_name_english': 'category', 'product_id': 'one_star'}, inplace=True)
    return lowest_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique",
        "price": "sum"
    })

    rfm_df.rename(columns={
        "order_purchase_timestamp": "max_order_timestamp",
        "order_id": "frequency",
        "price": "monetary"
    }, inplace=True)

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    new_rfm_df = rfm_df.drop('max_order_timestamp', axis=1)
    
    return new_rfm_df

all_df = pd.read_csv("dashboard/all_data.csv") 

datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date', 'delivery_time', 'shipping_limit_date']
all_df.sort_values(by='order_approved_at', inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column], format='mixed')

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.title("E-commerce")

    start_date, end_date = st.date_input(
        label="Range Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

sum_order_item_df = create_sum_order_items_df(main_df)
cust_bycity_df = create_cust_bycity_df(main_df)
cust_bystate_df = create_cust_bystate_df(main_df)
seller_bycity_df = create_seller_bycity_df(main_df)
seller_bystate_df = create_seller_bystate_df(main_df)
highest_df = create_highest_rating_df(main_df)
lowest_df = create_lowest_rating_df(main_df)
rfm_df = create_rfm_df(main_df)


st.title('E-Commerce Dashboard 📊')
colors = ["#6A9C89", "#C4DAD2", "#C4DAD2", "#C4DAD2", "#C4DAD2","#C4DAD2", "#C4DAD2", "#C4DAD2", "#C4DAD2", "#C4DAD2"]



st.subheader('Penjualan Kategori Produk')
tab1, tab2 = st.tabs(["Terbaik", "Terburuk"])
with tab1:    
    canvas, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(x="product_count", y="category", data=sum_order_item_df.head(10), palette=colors, hue="category", ax=ax)
    ax.set_title("Kategori Terbaik", loc="center", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis ='y', labelsize=18)
    st.pyplot(canvas)

with tab2:
    canvas, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(x="product_count", y="category", data=sum_order_item_df.sort_values(by="product_count", ascending=True).head(10), palette=colors, hue="category", ax=ax)
    ax.set_title("Kategori Terburuk", loc="center", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=18)
    st.pyplot(canvas)



st.subheader('Sebaran Demografis')
tab1, tab2 = st.tabs(["Customer", "Seller"])
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        canvas, ax = plt.subplots(figsize=(18, 15))
        sns.barplot(x="customer_count", 
                    y="customer_state", 
                    data=cust_bystate_df.sort_values(by="customer_count", ascending=False).head(10), 
                    palette=colors, 
                    hue="customer_state", 
                    ax=ax)
        ax.set_title("Sebaran Berdasarkan Negara Bagian", loc="center", fontsize=22)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis ='y', labelsize=20)
        st.pyplot(canvas)

    with col2:
        canvas, ax = plt.subplots(figsize=(18, 15))
        sns.barplot(x="customer_count", 
                    y="customer_city", 
                    data=cust_bycity_df.sort_values(by="customer_count", ascending=False).head(10), 
                    palette=colors, 
                    hue="customer_city", 
                    ax=ax)
        ax.set_title("Sebaran Berdasarkan Kota", loc="center", fontsize=22)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis ='y', labelsize=20)
        st.pyplot(canvas)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        canvas, ax = plt.subplots(figsize=(18, 15))

        sns.barplot(x="seller_count", 
                    y="seller_state", 
                    data=seller_bystate_df.sort_values(by="seller_count", ascending=False).head(10), 
                    palette=colors, 
                    hue="seller_state", 
                    ax=ax)
        ax.set_title("Sebaran Berdasarkan Negara Bagian", loc="center", fontsize=22)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis ='y', labelsize=20)
        st.pyplot(canvas)

    with col2:
        canvas, ax = plt.subplots(figsize=(18, 15))
        sns.barplot(x="seller_count", 
                    y="seller_city", 
                    data=seller_bycity_df.sort_values(by="seller_count", ascending=False).head(10), 
                    palette=colors, 
                    hue="seller_city", 
                    ax=ax)
        ax.set_title("Sebaran Berdasarkan Kota", loc="center", fontsize=22)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis ='y', labelsize=20)
        st.pyplot(canvas)



st.subheader('Rating Kategori Produk')
tab1, tab2 = st.tabs(["⭐⭐⭐⭐⭐", "⭐"])
with tab1:
    canvas, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(x="five_star", 
                y="category", 
                data=highest_df.sort_values(by="five_star", ascending=False).head(10), 
                palette=colors, 
                hue="category", 
                ax=ax)
    ax.set_title("Review Score 5", loc="center", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis ='y', labelsize=18)
    st.pyplot(canvas)

with tab2:
    canvas, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(x="one_star", 
                y="category", 
                data=lowest_df.sort_values(by="one_star", ascending=False).head(10), 
                palette=colors, 
                hue="category", 
                ax=ax)
    ax.set_title("Review Score 1", loc="center", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis ='y', labelsize=18)
    st.pyplot(canvas)



st.header('Top Customer')
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric(label="Rata-rata Recency (hari)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric(label="Rata-rata Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), 'BRL', locale='pt_BR')
    st.metric(label="Rata-rata Monetary", value=avg_monetary)

canvas, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#6A9C89", "#6A9C89", "#6A9C89", "#6A9C89", "#6A9C89"]

sns.barplot(y="recency", 
            x="customer_id", 
            data=rfm_df.sort_values(by="recency", ascending=True).head(5), 
            palette=colors, 
            ax=ax[0])
ax[0].set_title("Recency (hari)", loc="center", fontsize=50)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, rotation=80)
 
sns.barplot(y="frequency", 
            x="customer_id", 
            data=rfm_df.sort_values(by="frequency", ascending=False).head(5), 
            palette=colors, 
            ax=ax[1])
ax[1].set_title("Frequency", loc="center", fontsize=50)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=80)
 
sns.barplot(y="monetary", 
            x="customer_id", 
            data=rfm_df.sort_values(by="monetary", ascending=False).head(5), 
            palette=colors, 
            ax=ax[2])
ax[2].set_title("Monetary", loc="center", fontsize=50)
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35, rotation=80)
 
st.pyplot(canvas)


st.caption('© 2024 Copyright: Ryn')