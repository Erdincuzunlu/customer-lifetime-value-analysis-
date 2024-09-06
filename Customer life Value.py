##### Customer Life Value ######
from itertools import repeat

### 1. Data preparing
### 2. Average Order Value(Average_order_value  = total_price / total_transaction)
### 3. Purchase Frequency ( Total_transaction / Total_number_of_customers)
### 4. Repeat Rate And Churn rate ( Birden fazla alışveriş yapan sayısı / Tüm müşteriler )
### 5. Profit margin ( Profit_margin = total_price * 0,10
### 6. Customer value ( customer_value = Average_order_value * purchase_frequency)
### 7. Customer Lifetime Value CLTV = (Customer_value / churn_rate) * profit_margin)
### 8. creating segmentaion
### 9 Creating functiozan.


import pandas as pd
from sklearn.preprocessing import MinMaxScaler

pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows" , None)
pd.set_option("display.float_format", lambda x: "%.5f" %  x)


df_ = pd.read_excel("/Users/erdinc/PycharmProjects/pythonProject4/RMF/online_retail_II.xlsx", sheet_name="Year 2009-2010")

df = df_.copy()
df.head()

df.isnull().sum()

#df = df[df["Invoice"].str.contains("C", na=False)]
#olmayanları getirmek için başına tilda ~ işareti koyarız...
df = df[~df["Invoice"].str.contains("C", na=False)]

df.describe().T

df = df[(df["Quantity"] > 0)]

df.dropna(inplace=True)

df["TotalPrice"] = df["Quantity"] * df["Price"]
### Toplam ne kadar bedel ödendiğini bulmak için...
df.head()

cltv_c = df.groupby("Customer ID").agg({"Invoice": lambda x: x.nunique(),
                                         "Quantity": lambda x: x.sum(),
                                         "TotalPrice": lambda x: x.sum()})


#### Şimdi burada 1. adımda nunique kullanırken müşterinin kaç adet eşsiz faturası transactionu var onu
### bulmak için yapıyoruz...

#### 2. adımda quantity içindekilerin toplamını alıyoruz çünkü tamamen analiz etmek görmek için birinci öncelik değil

### 3. key value de total price'ın da sum toplamını alıyoruz...

cltv_c.columns ### dediğimizde listenin içinde ki isimler gelecek . Bu isimleri kendimize göre değiştirelim

cltv_c.columns = ["total_transaction", "total_unit", "total_price"]

#### Average order Value....
#### Average_order_value = total_price/ total_transaction

cltv_c.head()

cltv_c["average_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]

#### purchase Frequency (total_transaction / total_number_of_customer
cltv_c.shape[0]
cltv_c["purchase_frequency"] = cltv_c["total_transaction"] / cltv_c.shape[0]

cltv_c.head()

### 4. Repeat Rate And Churn rate ( Birden fazla alışveriş yapan sayısı / Tüm müşteriler )

cltv_c[cltv_c["total_transaction"] > 1].shape[0]
### birden fazla alışveriş yapan müşterilerin sayısı....

repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]

churn_rate = 1 - repeat_rate


### 5. Profit margin ( Profit_margin = total_price * 0,10)

cltv_c["profit_margin"] = cltv_c["total_price"] * 0.10


### 6. Customer value ( customer_value = Average_order_value * purchase_frequency)

cltv_c["Customer_value"] = cltv_c["average_order_value"] * cltv_c["purchase_frequency"]


### 7. Customer Lifetime Value CLTV = (Customer_value / churn_rate) * profit_margin)

cltv_c["CLTV"] = ((cltv_c["Customer_value"] / churn_rate) * cltv_c["profit_margin"])

cltv_c.sort_values(by="CLTV", ascending=False).head()

### 8. creating segmentaion

cltv_c.sort_values(by="CLTV", ascending=False).head()
cltv_c.sort_values(by="CLTV", ascending=False).tail()

#### 4 gruba ayıralım.. ve Analiz edelim qcut fonksiyonu ile...

cltv_c["segment"] = pd.qcut(cltv_c["CLTV"], 4, labels=["D", "C", "B", "A"])

cltv_c.sort_values(by="CLTV", ascending=False).head()

cltv_c.groupby("segment").agg({"count", "mean", "sum"})

### 9 . Tüm işlemlerin Fonksiyonlaştırılması....

def create_cltv_c(dataframe, profit=0.10):
    # Veriyi hazırlama
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe["Quantity"] > 0)]
    dataframe.dropna(inplace=True)
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    # Müşteri bazında toplama işlemleri
    cltv_c = dataframe.groupby("Customer ID").agg({
        "Invoice": lambda x: x.nunique(),
        "Quantity": lambda x: x.sum(),
        "TotalPrice": lambda x: x.sum()
    })
    cltv_c.columns = ["total_transaction", "total_unit", "total_price"]
    # Average Order Value
    cltv_c["average_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]
    # Purchase Frequency
    cltv_c["purchase_frequency"] = cltv_c["total_transaction"] / cltv_c.shape[0]
    # Repeat Rate ve Churn Rate
    repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]
    churn_rate = 1 - repeat_rate
    # Profit Margin
    cltv_c["profit_margin"] = profit
    # Customer Value
    cltv_c["Customer_value"] = cltv_c["average_order_value"] * cltv_c["purchase_frequency"]
    # Customer Lifetime Value
    cltv_c["CLTV"] = ((cltv_c["Customer_value"] / churn_rate) * cltv_c["profit_margin"])
    # Segmentasyon
    cltv_c["segment"] = pd.qcut(cltv_c["CLTV"], 4, labels=["D", "C", "B", "A"])

    return cltv_c

df = df_.copy()

clv = create_cltv_c(df)