import streamlit as st

def show():
    st.title("Accounting & Finance Review Committee")
    st.write("Welcome to the home page!")

    st.write("""
    ## このWebアプリケーションでできること

    このアプリケーションは、財務データの分析と可視化を行うためのツールです。以下の機能があります：

    1. **Page 1** - 既存の有価証券の財務データの分析：
        - 有価証券の財務指標を計算し、スコアリングします。
        - 各企業の財務指標を比較するためのレーダーチャートを表示します。
        - トップ10の企業を指標ごとにリストアップします。

    2. **Page 2** - 購入検討中の有価証券の分析：
        - 購入検討中の有価証券の財務指標を分析し、スコアリングします。
        - 購入株数や購入金額を基に推定購入金額と推定配当金額を計算します。
        - 各企業の財務指標を比較するためのレーダーチャートを表示します。

    3. **Page 3** - 有価証券の買い替えシミュレーション：
        - 現在保有している有価証券を売却し、新しい有価証券を購入した際の時価及び配当金をシミュレートします。
        　その際、法人税を30%と見積もって、実質購入金額=時価総額×0.7を想定しています。
        - 時価総額の比較のグラフにおいて、実質購入金額を想定しており、基本的に買い替え後の方が低くなります。また、その差額が決算書の有価証券評価損益に影響する可能性のある金額です。
        - 配当金の比較グラフは、保有している有価証券は2020年～2023年の実績値、新規の有価証券は2024年3月実績値で算出しています。

    """)

    st.write("## スコアリングの説明")
    
    st.write("""
    ### 自己資本比率スコア
    - 80%以上: 5点
    - 60%以上: 4点
    - 40%以上: 3点
    - 20%以上: 2点
    - 20%未満: 1点
    """)
    
    st.write("""
    ### ROEスコア
    - 15%以上: 5点
    - 10%以上: 4点
    - 5%以上: 3点
    - 2%以上: 2点
    - 2%未満: 1点
    """)

    st.write("""
    ### ROAスコア
    - 10%以上: 5点
    - 7.5%以上: 4点
    - 5%以上: 3点
    - 2.5%以上: 2点
    - 2.5%未満: 1点
    """)

    st.write("""
    ### PERスコア
    - 10倍未満: 5点
    - 15倍未満: 4点
    - 20倍未満: 3点
    - 25倍未満: 2点
    - 25倍以上: 1点
    """)

    st.write("""
    ### PBRスコア
    - 1倍未満: 5点
    - 2倍未満: 4点
    - 3倍未満: 3点
    - 4倍未満: 2点
    - 4倍以上: 1点
    """)

    st.write("""
    ### 配当利回りスコア
    - 5%以上: 5点
    - 4%以上: 4点
    - 3%以上: 3点
    - 2%以上: 2点
    - 2%未満: 1点
    """)

if __name__ == "__main__":
    show()
