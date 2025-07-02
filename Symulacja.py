import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PIL import Image
import numpy as np
import seaborn as sns
import matplotlib.cm as cm

# Wczytaj logo
logo = Image.open("logo.png")
st.sidebar.image(logo, width=150)  #
st.image(logo, width=200)  # Możesz dostosować szerokość (np. width=150)

# --- Tytuł ---
st.title("📊 Symulacja wzrostu przychodów dla Xopero Software S.A.")

st.markdown("""
Wybierz z panelu po lewej stronie interesujące Ciebie parametry.
""")

# --- Parametry początkowe ---
initial_clients = 504
initial_monthly_revenue = 570_000
initial_arpu = initial_monthly_revenue / initial_clients

# --- Sidebar parametry ---
st.sidebar.header("🔧 Parametry symulacji")
annual_goal = st.sidebar.number_input("🎯 Roczny cel przychodu (zł)", min_value=1_000_000, step=1_000_000, value=40_000_000)
new_clients = st.sidebar.slider("📈 Nowi klienci / mies.", 0, 400, 26, step=1)
churn_clients = st.sidebar.slider("📉 Klienci odchodzący / mies.", 0, 200, 8, step=1)
arpu = st.sidebar.slider("💰 Średni przychód na klienta (zł)", 500.0, 5000.0, round(initial_arpu, 2), step=100.0)
sales_costs = st.sidebar.slider("💸 Koszty sprzedaży (zł/mies.)", 100_000, 1_000_000, 203_000, step=10_000)

# --- Obliczenia ---
months = []
clients = []
monthly_revenues = []
annualized_revenues = []
cacs = []
paybacks = []

current_clients = initial_clients
month = 0
max_months = 240

while month < max_months:
    monthly_revenue = current_clients * arpu
    annualized_revenue = monthly_revenue * 12

    # Oblicz CAC
    if month < 5:
        cac = 7900
    else:
        cac = sales_costs / new_clients if new_clients > 0 else 0

    # Payback (miesiące) = CAC / ARPU
    payback = cac / arpu if arpu > 0 else 0

    # Zapis danych
    months.append(month)
    clients.append(current_clients)
    monthly_revenues.append(monthly_revenue)
    annualized_revenues.append(annualized_revenue)
    cacs.append(cac)
    paybacks.append(payback)

    if annualized_revenue >= annual_goal:
        break

    current_clients = max(current_clients + new_clients - churn_clients, 0)
    month += 1

# --- DataFrame ---
df = pd.DataFrame({
    "Miesiąc": months,
    "Liczba klientów": clients,
    "Miesięczny przychód": monthly_revenues,
    "Roczny przychód": annualized_revenues,
    "CAC": cacs,
    "Payback (miesięcy)": paybacks
})

# --- Komunikat ---
st.subheader("📈 Wynik symulacji")
if annualized_revenues[-1] >= annual_goal:
    st.success(f"✅ Cel osiągnięto w miesiącu **{months[-1]}** "
               f"przy miesięcznym przychodzie {int(monthly_revenues[-1]):,} zł "
               f"(roczny = {int(annualized_revenues[-1]):,} zł).")
else:
    st.error("❌ Nie udało się osiągnąć celu w ciągu 20 lat.")

# --- Wykres 1: liczba klientów ---
fig1, ax1 = plt.subplots()
ax1.plot(df["Miesiąc"], df["Liczba klientów"], color='#219ebc')
ax1.set_title("Liczba klientów w czasie")
ax1.set_xlabel("Miesiąc")
ax1.set_ylabel("Liczba klientów")
ax1.grid(False)
st.pyplot(fig1)

# --- Wykres 2: miesięczny przychód ---
fig2, ax2 = plt.subplots()
ax2.plot(df["Miesiąc"], df["Miesięczny przychód"], color='#219ebc')
ax2.axhline(annual_goal / 12, color='red', linestyle='--', label='Cel miesięczny')
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1_000_000:.1f} mln zł'))
ax2.set_title("Miesięczny przychód")
ax2.set_xlabel("Miesiąc")
ax2.set_ylabel("Przychód (mln zł)")
ax2.legend()
ax2.grid(False)
st.pyplot(fig2)

# --- Wykres 3: CAC ---
fig3, ax3 = plt.subplots()
ax3.plot(df["Miesiąc"], df["CAC"], color='#219ebc')
ax3.set_title("CAC (Koszt pozyskania klienta)")
ax3.set_xlabel("Miesiąc")
ax3.set_ylabel("CAC (zł)")
ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1000:.1f} tys. zł'))
ax3.set_ylim(bottom=0)
ax3.grid(False)
st.pyplot(fig3)

# --- Wykres 4: Payback ---
fig4, ax4 = plt.subplots()
ax4.plot(df["Miesiąc"], df["Payback (miesięcy)"], color='#219ebc')
ax4.set_title("CAC Payback Period (miesięcy)")
ax4.set_xlabel("Miesiąc")
ax4.set_ylabel("Payback (mies.)")
ax4.set_ylim(bottom=0)
ax4.grid(False)
st.pyplot(fig4)


with st.expander("📊 Dane szczegółowe (kliknij, aby rozwinąć)"):
    st.subheader("Szczegółowa tabela danych")
    st.dataframe(df, use_container_width=True)
    st.markdown("Możesz tu dodać dodatkowe analizy, komentarze, wykresy itd.")

# --- LTV i analiza wrażliwości ---
st.subheader("📌 Analiza LTV (Customer Lifetime Value)")

# Suwak: Marża brutto
gross_margin = st.sidebar.slider("📊 Marża brutto", 0.0, 1.0, 0.5, step=0.05)

# Oblicz churn rate na podstawie liczby klientów
churn_rate = churn_clients / current_clients if current_clients > 0 else 0.01
churn_rate = max(churn_rate, 0.0001)  # Zapobieganie dzieleniu przez zero

# Oblicz LTV
ltv = (arpu * gross_margin) / churn_rate if churn_rate > 0 else 0
ltv_cac_ratio = ltv / cacs[-1] if cacs[-1] > 0 else 0

st.markdown(f"""
- 📉 **Churn rate:** `{churn_rate:.2%}`
- 💰 **LTV:** `{ltv:,.2f} zł`
- 📊 **LTV / CAC:** `{ltv_cac_ratio:.2f}`
""")

# --- Wykres: LTV / CAC w czasie ---
ltvs = []
ltv_cac_ratios = []

for cac in cacs:
    ltv_val = (arpu * gross_margin) / churn_rate if churn_rate > 0 else 0
    ltvs.append(ltv_val)
    ratio = ltv_val / cac if cac > 0 else 0
    ltv_cac_ratios.append(ratio)

fig5, ax5 = plt.subplots()
ax5.plot(df["Miesiąc"], ltv_cac_ratios, color='#219ebc')
ax5.axhline(3, color='red', linestyle='--', label='Wartość docelowa (3x)')
ax5.set_title("Wskaźnik LTV / CAC w czasie")
ax5.set_xlabel("Miesiąc")
ax5.set_ylabel("LTV / CAC")
ax5.grid(False)
ax5.legend()
st.pyplot(fig5)


st.subheader("Analiza wrażliwości LTV: marża brutto vs churn rate")

# Parametry do analizy
arpu_selected = arpu  # z suwaka
margin_range = np.arange(1.0, 0.09, -0.1)   # 100% do 10% (odwrócony)
churn_range = np.arange(0.02, 0.18, 0.02)   # 2% do 16%

# Tworzenie macierzy LTV
ltv_matrix = []
for m in margin_range:
    row = []
    for c in churn_range:
        ltv_val = (arpu_selected * m) / c
        row.append(round(ltv_val))
    ltv_matrix.append(row)

# Konwersja do DataFrame
ltv_df = pd.DataFrame(ltv_matrix,
                      index=[f"{int(m*100)}%" for m in margin_range],
                      columns=[f"{int(c*100)}%" for c in churn_range])

# Wyświetlenie jako heatmapa z nową kolorystyką
st.markdown(f"Przy wybranym ARPU: **{arpu_selected:.2f} zł**")

fig8, ax8 = plt.subplots(figsize=(10, 6))
sns.heatmap(
    ltv_df,
    annot=True,
    fmt="d",
    cmap="YlOrBr",  # Zbliżona do skali z obrazka
    cbar_kws={'label': 'LTV (zł)'}
)
ax8.set_xlabel("Churn rate")
ax8.set_ylabel("Marża brutto")
ax8.set_title("Analiza wrażliwości LTV (im ciemniejszy kolor, tym wyższe LTV)")
st.pyplot(fig8)