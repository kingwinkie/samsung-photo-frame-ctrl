import streamlit as st
import config
import iface
def main():
    global slideShow
    
    
   # global user_input
    st.title('Photo frame remote')
    #st.write( st.session_state['my_data'])
    quit = st.button("Quit")
    if quit:
        iface.interface.quit = True
    blank = st.button("Blank")
    if blank:
        iface.interface.blank = True
    
    user_input = st.text_input("Insert coin")
    iface.interface.pr(user_input)
    # Add more Streamlit components here
    config.DELAY = st.text_input("Delay: ", value=config.DELAY)
    
if __name__ == '__main__':
    main()
