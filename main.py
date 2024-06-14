import streamlit as st
import home
import page1
import page2
import page3
import streamlit as st
import pandas as pd


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Page 1", "Page 2","Page 3"])

    if page == "Home":
        home.show()
    elif page == "Page 1":
        page1.show()
    elif page == "Page 2":
        page2.show()
    elif page == "Page 3":
        page3.show()


if __name__ == "__main__":
    main()
