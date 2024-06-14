import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import os

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
    st.title("Page 1")
    st.write("保有している有価証券を比較しましょう！")

    # ファイルアップロード
    uploaded_file = st.sidebar.file_uploader("エクセルファイルをアップロード", type="xlsx")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name='分析事項_有価証券(貼付用)')
        st.session_state['page1_data'] = df

    if 'page1_data' in st.session_state:
        df = st.session_state['page1_data']
        st.write("アップロードされたデータ:")
        st.dataframe(df)

        # 配当利回りの過去データを削除
        years_to_drop = [str(year) for year in range(2020, 2025)]
        for year in years_to_drop:
            column_name = f"配当利回り{year}"
            if column_name in df.columns:
                df = df.drop(columns=[column_name])

        # 配当利回りの値に100を掛けてパーセンテージ表示に変換し、小数点第2位まで四捨五入
        if '配当利回り' in df.columns:
            df['配当利回り'] = (df['配当利回り'] * 100).round(2)

        # スコアを計算
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

        def display_top_10(df, column, label):
            st.write(f"トップ10企業（{label}）")
            top_10_df = df.nlargest(10, column)
            st.dataframe(top_10_df[['企業名', column]])
        
        display_top_10(combined_df, '自己資本比率', '自己資本比率')
        display_top_10(combined_df, 'ROE', 'ROE')
        display_top_10(combined_df, 'ROA', 'ROA')
        display_top_10(combined_df, 'PER', 'PER')
        display_top_10(combined_df, 'PBR', 'PBR')
        display_top_10(combined_df, '配当利回り', '配当利回り')

        companies = combined_df['企業名'].unique()
        selected_companies = st.sidebar.multiselect("企業を選択", companies)

        size_option = st.sidebar.selectbox("レーダーチャートのサイズを選択", ["小", "中", "大"])
        if size_option == "小":
            chart_size = (4, 4)
            label_size = 6
        elif size_option == "中":
            chart_size = (6, 6)
            label_size = 8
        else:
            chart_size = (8, 8)
            label_size = 10

        # 同じレーダーチャートに複数の企業のデータを重ねて表示する関数
        def plot_radar_chart_multiple(data, categories, titles):
            N = len(categories)
            angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=chart_size, subplot_kw=dict(polar=True))

            prop = fm.FontProperties(fname=font_path)  # Windowsの場合

            for idx, d in enumerate(data):
                values = d.tolist()
                values += values[:1]
                ax.plot(angles, values, linewidth=1.5, linestyle='solid', label=titles[idx])
                ax.fill(angles, values, alpha=0.25)

                # スコアの表示
                for angle, value in zip(angles, values):
                    ax.text(angle, value * 1.1, str(value), horizontalalignment='center', size=12, color='black', fontproperties=prop)

            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontproperties=prop)
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.3), prop=prop, fontsize=label_size)

            st.pyplot(fig)

        # 横並びにレーダーチャートを表示する関数
        def plot_radar_charts_side_by_side(data, categories, titles):
            num_charts = len(data)
            num_rows = (num_charts + 1) // 2  # 列数を2に設定
            fig, axes = plt.subplots(num_rows, 2, subplot_kw=dict(polar=True), figsize=(chart_size[0] * 2, chart_size[1] * num_rows * 1.5))

            prop = fm.FontProperties(fname=font_path)

            for idx, ax in enumerate(axes.flat):
                if idx < num_charts:
                    values = data[idx].tolist()
                    values += values[:1]
                    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
                    angles += angles[:1]

                    ax.fill(angles, values, color='blue', alpha=0.25)
                    ax.plot(angles, values, color='blue', linewidth=2)
                    ax.set_yticklabels([])
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(categories, fontproperties=prop)
                    ax.set_title(f"{titles[idx]} (合計スコア: {sum(values[:-1])})", size=20, fontproperties=
prop, pad=30)

                    for angle, value in zip(angles, values):
                        ax.text(angle, value * 1.1, str(value), horizontalalignment='center', size=12, color='black', fontproperties=prop)

                else:
                    ax.axis('off')

            plt.tight_layout(pad=5.0)  # レイアウトのパディングを増やしてスペースを広げる
            st.pyplot(fig)

        # 選択された企業のレーダーチャートを表示
        if selected_companies:
            categories = score_columns
            data = []
            titles = []
            for company in selected_companies:
                company_data = combined_df[combined_df['企業名'] == company]
                company_scores = company_data[categories].iloc[0]
                data.append(company_scores)
                titles.append(company)
            
            # 横並びに表示
            st.write("横並びのレーダーチャート")
            plot_radar_charts_side_by_side(data, categories, titles)

            # 重ねて表示
            st.write("重ねたレーダーチャート")
            plot_radar_chart_multiple(data, categories, titles)

        # 業種ごとのスコア平均を表示
        industry_option = st.sidebar.selectbox("業種ごとのスコア平均を表示", ["なし", "業種別スコア"])
        
        if industry_option == "業種別スコア":
            st.write("業種別スコア平均")
            industry_means = combined_df.groupby('業種')[score_columns].mean()
            st.dataframe(industry_means)

            for industry in industry_means.index:
                st.write(f"業種: {industry} 業種別スコア平均")
                industry_scores = industry_means.loc[industry]

                # 業種別スコア平均のレーダーチャートを表示
                plot_radar_chart_multiple([industry_scores], score_columns, [f"{industry} 業種別スコア平均"])

if __name__ == "__main__":
    show()
