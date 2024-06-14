import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# フォントファイルのパスを指定
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'msgothic.ttc')
prop = fm.FontProperties(fname=font_path)


def show():
    # Session stateからPage1とPage2のデータを取得
    page1_df = st.session_state.get('page1_data')
    page2_df = st.session_state.get('page2_data')

    if page1_df is None or page2_df is None:
        st.error("Page1とPage2のデータが必要です。データをアップロードしてください。")
    else:
        st.title("有価証券の買い替えシミュレーション")

        # 保有する有価証券を複数選択
        held_securities = st.multiselect("保有する有価証券を選択", page1_df['企業名'])

        if not held_securities:
            st.error("少なくとも1つの保有有価証券を選択してください。")
            return

        # 保有有価証券のデータを取得
        held_security_data = page1_df[page1_df['企業名'].isin(held_securities)]

        # 2020～2023年の配当金の平均を算出
        held_security_data['配当金平均'] = held_security_data[['配当金2020', '配当金2021', '配当金2022', '配当金2023']].mean(axis=1)

        # 保有有価証券の時価総額の合計
        held_market_value = held_security_data['時価'].sum()
        st.write(f"選択した保有有価証券の時価総額: {held_market_value:,.0f} 円")

        # 時価の3割減少した金額を上限
        max_purchase_amount = held_market_value * 0.7
        st.write(f"購入可能な上限金額（時価の3割減少した金額）: {max_purchase_amount:,.0f} 円")

        # 購入金額のスライダー（100万円単位）
        purchase_amount = st.slider("購入金額", min_value=0, max_value=int(max_purchase_amount), step=1000000, format="%d")
        st.write(f"選択された購入金額: {purchase_amount:,} 円")

        # 買い替え先の有価証券を選択
        new_security = st.selectbox("買い替え先の有価証券を選択", page2_df['企業名'])

        # 買い替え先有価証券のデータを取得
        new_security_data = page2_df[page2_df['企業名'] == new_security].iloc[0]

        # 新しい有価証券の購入株数
        new_purchase_shares = purchase_amount // new_security_data['株価']

        # 新しい有価証券の配当金
        new_dividends = new_purchase_shares * new_security_data['1株当たり配当金']

        # 結果をテーブル形式で表示
        result_data = {
            '項目': ['新しい有価証券の購入株数', '新しい有価証券の配当金'],
            '値': [f'{new_purchase_shares:,} 株', f'{new_dividends:,.0f} 円']
        }
        result_df = pd.DataFrame(result_data)
        st.write("### 買い替えシミュレーション結果")
        st.table(result_df)

        # 保有有価証券ごとの計算結果をテーブル形式で表示
        held_securities_data = []
        for _, row in held_security_data.iterrows():
            held_securities_data.append({
                '企業名': row['企業名'],
                '時価': f"{row['時価']:,.0f} 円",
                '配当金平均': f"{row['配当金平均']:,.0f} 円"
            })

        detailed_df = pd.DataFrame(held_securities_data)
        st.write("### 保有有価証券ごとの計算結果")
        st.table(detailed_df)

        # グラフやテーブルで結果を視覚的に表示
        st.write("### 時価総額の比較")
        fig, ax = plt.subplots()
        categories = [', '.join(held_securities), new_security]
        values = [held_market_value / 1e6, new_purchase_shares * new_security_data['株価'] / 1e6]  # 百万円単位に変換
        bars = ax.bar(categories, values, color=['blue', 'green'])
        ax.set_ylabel('価格（百万円）')
        ax.set_xticklabels(categories)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
        st.pyplot(fig)

        st.write("### 配当金の比較")
        fig, ax = plt.subplots()
        categories = [', '.join(held_securities), new_security]
        values = [held_security_data['配当金平均'].sum(), new_dividends]  # 円単位
        bars = ax.bar(categories, values, color=['blue', 'green'])
        ax.set_ylabel('配当金（円）')
        ax.set_xticklabels(categories)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
        st.pyplot(fig)

        # 計算結果のテーブル表示
        st.write("### 計算結果")
        result_df = pd.DataFrame({
            '項目': ['時価総額', '配当金'],
            f'保有有価証券（{", ".join(held_securities)}）': [held_market_value, held_security_data['配当金平均'].sum()],
            f'新しい有価証券（{new_security}）': [new_purchase_shares * new_security_data['株価'], new_dividends],
            '変化': [(new_purchase_shares * new_security_data['株価']) - held_market_value, new_dividends - held_security_data['配当金平均'].sum()]
        })
        result_df[f'保有有価証券（{", ".join(held_securities)}）'] = result_df[f'保有有価証券（{", ".join(held_securities)}）'].apply(lambda x: f'{x:,.0f} 円')
        result_df[f'新しい有価証券（{new_security}）'] = result_df[f'新しい有価証券（{new_security}）'].apply(lambda x: f'{x:,.0f} 円')
        result_df['変化'] = result_df['変化'].apply(lambda x: f'{x:,.0f} 円')
        st.dataframe(result_df)

if __name__ == "__main__":
    show()
