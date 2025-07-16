import streamlit as st

st.title("Hello Streamlit on App Runner! 👋")

option = st.selectbox(
    "What would you like to do?",
    ("Say Hello", "Say Goodbye")
)

if option == "Say Hello":
    st.write("👋 Hello there!")
else:
    st.write("👋 Goodbye!")