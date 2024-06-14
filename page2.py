import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# フォントファイルのパスを指定
font_path = 'msgothic.ttc'

# スコアリングのための関数
def calculate_self_capital_ratio_score(value):
    if pd.isna(value):
        return None
    elif value >= 80:
        return 5
    elif value >= 60:
        return 4
    elif value >= 40:
        return 3
    elif value >= 20:
        return 2
    else:
        return 1

def calculate_roe_score(value):
    if pd.isna(value):
        return None
    elif value >= 15:
        return 5
    elif value >= 10:
        return 4
    elif value >= 5:
        return 3
    elif value >= 2:
        return 2
    else:
        return 1

def calculate_roa_score(value):
    if pd.isna(value):
        return None
    elif value >= 10:
        return 5
    elif value >= 7.5:
        return 4
    elif value >= 5:
        return 3
    elif value >= 2.5:
        return 2
    else:
        return 1

def calculate_per_score(value):
    if pd.isna(value):
        return None
    elif value < 10:
        return 5
    elif value < 15:
        return 4
    elif value < 20:
        return 3
    elif value < 25:
        return 2
    else:
        return 1

def calculate_pbr_score(value):
    if pd.isna(value):
        return None
    elif value < 1:
        return 5
    elif value < 2:
        return 4
    elif value < 3:
        return 3
    elif value < 4:
        return 2
    else:
        return 1

def calculate_dividend_yield_score(value):
    if pd.isna(value):
        return None
    elif value >= 5:
        return 5
    elif value >= 4:
        return 4
    elif value >= 3:
        return 3
    elif value >= 2:
        return 2
    else:
        return 1

def show():
    st.title("Page 2")
    st.write("有価証券を検討しましょう!")

    # ファイルアップロード
    uploaded_file = st.sidebar.file_uploader("エクセルファイルをアップロード", type="xlsx")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name='分析事項_購入検討有価証券')
        st.session_state['page2_data'] = df

    if 'page2_data' in st.session_state:
        df = st.session_state['page2_data']
        st.write("アップロードされたデータ:")
        st.dataframe(df)

        # 必要な列を数値型に変換
        numeric_columns = ['自己資本比率', 'ROE', 'ROA', 'PER', 'PBR', '配当利回り', '株価', '1株当たり配当金', '購入株数']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # A〜H列の処理（Page1と同様）
        df['配当利回り'] = (df['配当利回り'] * 100).round(2)

        def calculate_scores(row):
            scores = {}
            scores['自己資本比率スコア'] = calculate_self_capital_ratio_score(row['自己資本比率'])
            scores['ROEスコア'] = calculate_roe_score(row['ROE'])
            scores['ROAスコア'] = calculate_roa_score(row['ROA'])
            scores['PERスコア'] = calculate_per_score(row['PER'])
            scores['PBRスコア'] = calculate_pbr_score(row['PBR'])
            scores['配当利回りスコア'] = calculate_dividend_yield_score(row['配当利回り'])
            return pd.Series(scores)

        scores_df = df.apply(calculate_scores, axis=1)
        combined_df = pd.concat([df, scores_df], axis=1)
        score_columns = ['自己資本比率スコア', 'ROEスコア', 'ROAスコア', 'PERスコア', 'PBRスコア', '配当利回りスコア']
        combined_df['合計スコア'] = combined_df[score_columns].sum(axis=1)

        st.write("企業の財務指標スコア一覧")
        st.dataframe(combined_df[['企業名'] + score_columns + ['合計スコア']])

        # 企業名の選択
        companies = combined_df['企業名'].unique()
        selected_companies = st.sidebar.multiselect("企業を選択", companies)

        # 購入株数の選択
        purchase_option = st.sidebar.selectbox("選択オプション", ["株数", "金額"])
        if purchase_option == "株数":
            num_stocks = st.sidebar.slider("購入株数", min_value=100, max_value=10000, step=100)
        else:
            amount = st.sidebar.slider("購入金額 (100万円単位)", min_value=100, max_value=10000, step=100) * 10000  # 万円単位から円単位に変換

        # 選択した企業と株数/金額に基づくデータのフィルタリング
        if selected_companies:
            filtered_df = combined_df[combined_df['企業名'].isin(selected_companies)]
            st.write("選択された企業のデータ")
            st.dataframe(filtered_df)

            if purchase_option == "株数":
                # 株数に基づく計算
                filtered_df['推定購入金額'] = filtered_df['株価'] * num_stocks
                filtered_df['推定配当金額'] = filtered_df['1株当たり配当金'] * num_stocks
            else:
                # 金額に基づく計算
                filtered_df['購入株数'] = (amount // filtered_df['株価']).astype(int)
                filtered_df['推定購入金額'] = filtered_df['株価'] * filtered_df['購入株数']
                filtered_df['推定配当金額'] = filtered_df['1株当たり配当金'] * filtered_df['購入株数']

            st.write("計算結果")
            st.dataframe(filtered_df[['企業名', '株価', '1株当たり配当金', '購入株数', '推定購入金額', '推定配当金額']])

            # レーダーチャートの作成
            st.write("企業ごとのスコアの可視化（レーダーチャート）")

            categories = score_columns
            num_vars = len(categories)

            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            prop = fm.FontProperties(fname=font_path)

            for idx, row in filtered_df.iterrows():
                values = row[score_columns].tolist()
                values += values[:1]
                angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
                angles += angles[:1]

                ax.plot(angles, values, linewidth=2, linestyle='solid', label=row['企業名'])
                ax.fill(angles, values, alpha=0.25)

                for i, angle in enumerate(angles):
                    if i < len(values):
                        ax.text(angle, values[i] * 1.1, str(values[i]), horizontalalignment='center', size=12, color='black', fontproperties=prop)

            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontproperties=prop)
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.3), prop=prop, fontsize=12)

            st.pyplot(fig)

            # スコアテーブルの表示
            st.write("企業ごとのスコア")
            st.dataframe(filtered_df[['企業名'] + score_columns + ['合計スコア']])

            # 株価の棒グラフ
            st.write("株価の比較（棒グラフ）")

            fig, ax = plt.subplots(figsize=(10, 6))
            index = np.arange(len(filtered_df))
            bar_width = 0.35

            bars1 = plt.bar(index, filtered_df['株価'].round(), bar_width, alpha=0.8, label='株価（円）', color='blue')

            plt.xlabel('企業名', fontproperties=prop)
            plt.ylabel('株価（円）', fontproperties=prop)
            plt.title('株価の比較', fontproperties=prop)
            plt.xticks(index, filtered_df['企業名'], rotation=45, fontproperties=prop)
            plt.legend(prop=prop)  # フォントプロパティを設定

            # データラベルを追加
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:,.0f}', ha='center', va='bottom', fontproperties=prop)

            plt.tight_layout()
            st.pyplot(fig)

            # 1株当たり配当金の棒グラフ
            st.write("1株当たり配当金の比較（棒グラフ）")

            fig, ax = plt.subplots(figsize=(10, 6))
            index = np.arange(len(filtered_df))
            bar_width = 0.35

            bars2 = plt.bar(index, filtered_df['1株当たり配当金'].round(), bar_width, alpha=0.8, label='1株当たり配当金（円）', color='green')

            plt.xlabel('企業名', fontproperties=prop)
            plt.ylabel('1株当たり配当金（円）', fontproperties=prop)
            plt.title('1株当たり配当金の比較', fontproperties=prop)
            plt.xticks(index, filtered_df['企業名'], rotation=45, fontproperties=prop)
            plt.legend(prop=prop)  # フォントプロパティを設定

            # データラベルを追加
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:,.0f}', ha='center', va='bottom', fontproperties=prop)

            plt.tight_layout()
            st.pyplot(fig)

            # 株価と1株当たり配当金の計算結果を表示
            st.write("株価と1株当たり配当金の計算結果")
            st.dataframe(filtered_df[['企業名', '株価', '1株当たり配当金']].style.format({'株価': '{:,.0f}', '1株当たり配当金': '{:,.0f}'}))

            # 推定購入金額と推定配当金額の棒グラフ
            st.write("推定購入金額と推定配当金額の比較（棒グラフ）")

            fig, ax = plt.subplots(figsize=(10, 6))
            index = np.arange(len(filtered_df))
            bar_width = 0.35

            bars3 = plt.bar(index, filtered_df['推定購入金額'].round(), bar_width, alpha=0.8, label='推定購入金額（円）', color='blue')
            bars4 = plt.bar(index + bar_width, filtered_df['推定配当金額'].round(), bar_width, alpha=0.8, label='推定配当金額（円）', color='green')

            plt.xlabel('企業名', fontproperties=prop)
            plt.ylabel('金額（円）', fontproperties=prop)
            plt.title('推定購入金額と推定配当金額の比較', fontproperties=prop)
            plt.xticks(index + bar_width / 2, filtered_df['企業名'], rotation=45, fontproperties=prop)
            plt.legend(prop=prop)  # フォントプロパティを設定

            # データラベルを追加
            for bar in bars3:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:,.0f}', ha='center', va='bottom', fontproperties=prop)
            for bar in bars4:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:,.0f}', ha='center', va='bottom', fontproperties=prop)

            plt.tight_layout()
            st.pyplot(fig)

            # 推定購入金額と推定配当金額の計算結果を表示
            st.write("推定購入金額と推定配当金額の計算結果")
            st.dataframe(filtered_df[['企業名', '推定購入金額', '推定配当金額']].style.format({'推定購入金額': '{:,.0f}', '推定配当金額': '{:,.0f}'}))

if __name__ == "__main__":
    show()
