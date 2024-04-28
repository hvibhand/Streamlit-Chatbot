import streamlit as st
from streamlit_chat import message

from client import get_response_from_client
from utils import calculate_cost_for_model
from utils import generate_deployed_models_dict
from utils import generate_page_header_html_content
from utils import get_default_messages
from utils import get_formatted_cost_message
from utils import get_formatted_total_cost_message

# Setting page title and header
st.set_page_config(page_title='SmartSwipe.io - by Team AI-Bytes', page_icon=':robot_face:')
st.markdown(generate_page_header_html_content(), unsafe_allow_html=True)

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = get_default_messages()
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Sidebar for Settings - let user choose genai, programming language accordingly
# it will show total cost of current conversation also user can clear the current conversation
st.sidebar.title('Settings')

deployed_models = generate_deployed_models_dict()
model_name = st.sidebar.radio('Choose Azure OpenAI model:', list(deployed_models.keys()))

languageMessages = get_default_messages()

counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button('Clear Conversation', key='clear')

# Map genai names to OpenAI genai IDs
model = deployed_models[model_name]

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = languageMessages
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({'role': 'user', 'content': prompt})

    completion = get_response_from_client(model, st.session_state['messages'])
    response = completion.choices[0].message.content
    st.session_state['messages'].append({'role': 'assistant', 'content': response})

    return response, completion.usage.total_tokens, completion.usage.prompt_tokens, completion.usage.completion_tokens


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area(
            label=f"Submit your query related with the Credit Cards transactions:",
            key='input',
            height=80)
        submit_button = st.form_submit_button(label='Submit')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)
        cost = calculate_cost_for_model(model_name, total_tokens, prompt_tokens, completion_tokens)
        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state['generated'][i], key=str(i))
            st.write(get_formatted_cost_message(
                model_name=st.session_state['model_name'][i],
                total_tokens=st.session_state['total_tokens'][i],
                cost=st.session_state['cost'][i])
            )
            counter_placeholder.write(get_formatted_total_cost_message(
                total_cost=st.session_state['total_cost'])
            )
