import streamlit as st
import mysql.connector
import requests
from chatbot import DualChatbot
from chatbot2 import Chatbot2
from streamlit_chat import message
import time
from gtts import gTTS
from io import BytesIO
from werkzeug.security import check_password_hash


# Database connection function for login validation
def validate_login(username, password):
    db = mysql.connector.connect(host="localhost", user="root", password="12345", database="streamlit_logins")
    cursor = db.cursor()

    # Fetch the hashed password from the database instead of comparing directly
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    stored_password = cursor.fetchone()

    db.close()

    # Check if a password was fetched and verify it against the provided password
    if stored_password and check_password_hash(stored_password[0], password):
        return True
    else:
        return False

# Initialize session state variables for user authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_details = {}
    st.sidebar.title("User Authentication")
    st.title("English Learning App 🌍📖🎓")

# User login and registration UI
if not st.session_state.logged_in:
    st.sidebar.subheader("Login")
    login_username = st.sidebar.text_input("Username")
    login_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if validate_login(login_username, login_password):
            st.success("Logged in successfully!")
            st.session_state.logged_in = True
            st.session_state.user_details['username'] = login_username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
    st.sidebar.subheader("Registration")
    register_username = st.sidebar.text_input("New username")
    register_password = st.sidebar.text_input("New password", type="password")
    if st.sidebar.button("Register"):
        response = requests.post("http://localhost:5000/register", data={"username": register_username, "password": register_password})
        if response.status_code == 200:
            st.sidebar.success("Registration successful")
        else:
            st.sidebar.error(response.text)
else:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
        st.session_state.user_details = {}
        st.experimental_rerun()

# Chatbot conversation UI
if st.session_state.logged_in:
    def convo():
        SESSION_LENGTHS = ['Short', 'Long']
        PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced']
        MAX_EXCHANGE_COUNTS = {'Short': {'Conversation': 8, 'Debate': 4}, 'Long': {'Conversation': 16, 'Debate': 8}}
        AVATAR_SEED = [123, 42]
        engine = 'OpenAI'
        st.markdown("Choose your desired settings and press 'Generate' to start 🚀")
        learning_mode = st.sidebar.selectbox('Learning Mode 📖', ('Conversation', 'Debate'))

        if learning_mode == 'Conversation':
            role1 = st.sidebar.text_input('Role of bot 1🤖: ')
            action1 = st.sidebar.text_input('Action of bot 1🔊: ')
            role2 = st.sidebar.text_input('Role of bot 2🤖:')
            action2 = st.sidebar.text_input('Action of bot 2🔊: ')
            scenario = st.sidebar.text_input('Place of the interaction🎬:  ')
            time_delay = 2
            role_dict = {'role1': {'name': role1, 'action': action1}, 'role2': {'name': role2, 'action': action2}}
        else:
            scenario = st.sidebar.text_input('Debate Topic:🗣️')
            role_dict = {'role1': {'name': 'Proponent'}, 'role2': {'name': 'Opponent'}}
            time_delay = 5

        session_length = st.sidebar.selectbox('Length of the session⌚: ', SESSION_LENGTHS)
        proficiency_level = st.sidebar.selectbox('English Level🎚️:', PROFICIENCY_LEVELS)

        if "bot1_mesg" not in st.session_state:
                st.session_state["bot1_mesg"] = []

        if "bot2_mesg" not in st.session_state:
                st.session_state["bot2_mesg"] = []

        if 'batch_flag' not in st.session_state:
                st.session_state["batch_flag"] = False

        # if 'translate_flag' not in st.session_state:
        #         st.session_state["translate_flag"] = False

        if 'audio_flag' not in st.session_state:
                st.session_state["audio_flag"] = False

        if 'message_counter' not in st.session_state:
                st.session_state["message_counter"] = 0


        def show_messages(mesg_1, mesg_2, message_counter,
                            time_delay, batch=False, audio=False):
                """Display conversation exchanges. This helper function supports
                displaying original texts, translated texts, and audio speech. 

                Args:
                --------
                mesg1: messages spoken by the first bot
                mesg2: messages spoken by the second bot
                message_counter: create unique ID key for chat messages
                time_delay: time interval between conversations
                batch: True/False to indicate if conversations will be shown
                    all together or with a certain time delay.
                audio: True/False to indicate if the audio speech need to
                    be appended to the texts  
                # translation: True/False to indicate if the translated texts need to
                #         be displayed    

                Output:
                -------
                message_counter: updated counter for ID key
                """    

                for i, mesg in enumerate([mesg_1, mesg_2]):
                    # Show original exchange ()
                    message(f"{mesg['content']}", is_user=i==1, avatar_style="bottts", 
                            seed=AVATAR_SEED[i],
                            key=message_counter)
                    message_counter += 1
                    
                    # Mimic time interval between conversations
                    # (this time delay only appears when generating 
                    # the conversation script for the first time)
                    if not batch:
                        time.sleep(time_delay)

                    # Show translated exchange
                    # if translation:
                    #     message(f"{mesg['translation']}", is_user=i==1, avatar_style="bottts", 
                    #                 seed=AVATAR_SEED[i], 
                    #                 key=message_counter)
                    #     message_counter += 1

                    # Append autio to the exchange
                    if audio:
                        tts = gTTS(text=mesg['content'], lang='en')  # Directly use 'en' for English
                        sound_file = BytesIO()
                        tts.write_to_fp(sound_file)
                        st.audio(sound_file)

                return message_counter


            # Define the button layout at the beginning
        audio_col = st.columns(1)[0]

            # Create the conversation container
        conversation_container = st.container()

        if 'dual_chatbots' not in st.session_state:

                if st.sidebar.button('Generate'):

                    # Add flag to indicate if this is the first time running the script
                    st.session_state["first_time_exec"] = True 

                    with conversation_container:
                        if learning_mode == 'Conversation':
                            st.write(f"""#### The following conversation happens between {role1} and {role2} in {scenario}.🎬""")

                        else:
                            st.write(f"""#### Debate 🗣️: {scenario}""")

                        # Instantiate dual-chatbot system
                        dual_chatbots = DualChatbot(engine, role_dict, "en", scenario, 
                                                    proficiency_level, learning_mode, session_length)
                        st.session_state['dual_chatbots'] = dual_chatbots
                        
                        # Start exchanges
                        for _ in range(MAX_EXCHANGE_COUNTS[session_length][learning_mode]):
                            output1, output2, _, _ = dual_chatbots.step()

                            mesg_1 = {"role": dual_chatbots.chatbots['role1']['name'], 
                                    "content": output1}
                            mesg_2 = {"role": dual_chatbots.chatbots['role2']['name'], 
                                    "content": output2}
                            
                            new_count = show_messages(mesg_1, mesg_2, 
                                                    st.session_state["message_counter"],
                                                    time_delay=time_delay, batch=False,
                                                    audio=False)
                            st.session_state["message_counter"] = new_count

                            # Update session state
                            st.session_state.bot1_mesg.append(mesg_1)
                            st.session_state.bot2_mesg.append(mesg_2)
                            


        if 'dual_chatbots' in st.session_state:  

                # # Show translation 
                # if translate_col.button('Translate to English'):
                #     st.session_state['translate_flag'] = True
                #     st.session_state['batch_flag'] = True

                # # Show original text
                # if original_col.button('Show original'):
                #     st.session_state['translate_flag'] = False
                #     st.session_state['batch_flag'] = True

                # Append audio
                if audio_col.button('Play audio'):
                    st.session_state['audio_flag'] = True
                    st.session_state['batch_flag'] = True

                # Retrieve generated conversation & chatbots
                mesg1_list = st.session_state.bot1_mesg
                mesg2_list = st.session_state.bot2_mesg
                dual_chatbots = st.session_state['dual_chatbots']
                
                # Control message appear
                if st.session_state["first_time_exec"]:
                    st.session_state['first_time_exec'] = False
                
                else:
                    # Show complete message
                    with conversation_container:
                        
                        if learning_mode == 'Conversation':
                            st.write(f"""#### {role1} and {role2} {scenario} 🎭""")

                        else:
                            st.write(f"""#### Debate 💬: {scenario}""")
                    
                        for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
                            new_count = show_messages(mesg_1, mesg_2, 
                                                    st.session_state["message_counter"],
                                                    time_delay=time_delay,
                                                    batch=st.session_state['batch_flag'],
                                                    audio=st.session_state['audio_flag'])
                                                    # translation=st.session_state['translate_flag']
                            st.session_state["message_counter"] = new_count
                

                # Create summary for key learning points
                summary_expander = st.expander('Key Learning Points')
                scripts = []
                for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
                    for i, mesg in enumerate([mesg_1, mesg_2]):
                        scripts.append(mesg['role'] + ': ' + mesg['content'])
                
                # Compile summary
                if "summary" not in st.session_state:
                    summary = dual_chatbots.summary(scripts)
                    st.session_state["summary"] = summary
                else:
                    summary = st.session_state["summary"]
                
                with summary_expander:
                    st.markdown(f"**Here is the learning summary:**")
                    st.write(summary)     

       

    # Function definitions for starting conversation and main app logic...
    def start_conversation():
        # Chatbot initialization and conversation start logic...
        global chatbot
        chatbot = Chatbot2('OpenAI')
        chatbot.start_conversation()
        response = chatbot.conversation.predict(input="This chatbot is designed to assist users in learning English through conversation. Act as a language teacher, make the answers easy to understand as the user's vocabulary is limited. Suggest to the users different scenarios or exercises to practice and give feedback")
        print("Chatbot response:", response)  # Print response for debugging
        st.session_state.chatbot = chatbot
        st.write("Chatbot response:", response)  # Display response in Streamlit


    def main():
        st.title("English Learning and Conversational Chatbot ")
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = None

        # Sidebar navigation
        navigation = st.sidebar.radio("Navigation", ["Interactional chatbot", "Duo chatbot"])


        # Main app logic including sidebar navigation and chatbot integration...
        if navigation == "Duo chatbot":
             convo()
        
        if navigation == "Interactional chatbot":
           st.title("Let's practice English!📚 ")


           if st.button("Start Conversation", key="start_button"):  # Unique key for button
             start_conversation()

            # Input field for the user to type messages
           user_input = st.text_input("You:", "")

    # Button to send the user message to the chatbot
           if st.button("Send"):
            if st.session_state.chatbot is None:
                st.error("Please start the conversation first.")
            else:
                # Get response from the chatbot
                response = st.session_state.chatbot.conversation.predict(input=user_input)
                st.text_area("Chatbot:", response, height=100)
             
             
        #    chatbot = Chatbot2('OpenAI')
    
    # Button to start the conversation
        

    if __name__ == "__main__":
        main()
