import csv
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import cv2
import base64
import pygame
import yaml

def read_config_yaml(file_path):
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config

st.set_page_config(layout="wide")
with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)



config = read_config_yaml('config.yaml')
BARCODE_HISTORY = config['BARCODE_HISTORY']
BARCODE_STATUS = config['BARCODE_STATUS']
BARCODE_RESET = config['BARCODE_RESET']
RIFLE_DATA_PATH = config['RIFLE_DATA_PATH']
PERSON_DATA_PATH = config['PERSON_DATA_PATH']
HISTORY_DATA = config['HISTORY_DATA']

if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "current_rifle" not in st.session_state:
    st.session_state.current_rifle = ""
if "current_person" not in st.session_state:
    st.session_state.current_person = ""

def example(color1, color2, color3, content):
     st.markdown(f'<p style="text-align:center;background-image: linear-gradient(to right,{color1}, {color2});color:{color3};font-size:36px;border-radius:0%;">{content}</p>', unsafe_allow_html=True)

def img_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    data_url = f"data:image/png;base64,{encoded_string}"
    return data_url

def toggle_instock(rifle_barcode):
    data = []
    sta = []
    with open(RIFLE_DATA_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  
        data = [header]  
        for row in reader:
            if row[0] == rifle_barcode:
                if row[3] == 'True':
                    row[3] = 'False'
                elif row[3] == 'False':
                    row[3] = 'True'
                sta = row[3]
            data.append(row)
    
    with open(RIFLE_DATA_PATH, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return sta

def submit():
    st.session_state.input_text = st.session_state.widget
    st.session_state.widget = ""


current_state = "โปรดแสกน Barcode"

#read data
df_rifle = pd.read_csv(RIFLE_DATA_PATH)
df_person = pd.read_csv(PERSON_DATA_PATH)
try:
    df_history = pd.read_csv(HISTORY_DATA)
except:
    df_history = pd.DataFrame(columns=[
        'rifle_barcode', 
        'rifle_respon_name', 
        'rifle_respon_id', 
        'person_id', 
        'person_barcode', 
        'person_name', 
        'timestamp', 
        'action'
    ])
    
df_history = df_history.sort_values(by='timestamp',ascending=False)

rifles_in = df_rifle[df_rifle['instock'] == True]['rifle_barcode'].tolist()
rifles_out = df_rifle[df_rifle['instock'] == False]['rifle_barcode'].tolist()

# input text
st.text_input("scan barcode", key="widget", on_change=submit)
input_text = st.session_state.input_text
st.components.v1.html(
    f"""
    <script>
        // Wait until the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', function() {{
            // Focus on the input field when the page loads
            var inputField = window.parent.document.querySelector('input[type="text"]');
            if(inputField) {{
                inputField.focus();
            }}
        }});
    </script>
    """,
    height=0,
)

## check text input
current_rifle = df_rifle[df_rifle['rifle_barcode']==input_text]
df_history_current_rifle_barcode = df_history[df_history['rifle_barcode']==input_text]
current_person = df_person[df_person['person_barcode']==input_text]
if current_rifle.shape[0]==1:
    st.session_state.current_rifle = dict(current_rifle.iloc[0])
if current_person.shape[0]==1:
    st.session_state.current_person = dict(current_person.iloc[0])

# history
if input_text == BARCODE_HISTORY:
    st.title('ประวัติการเบิกจ่ายอาวุธ')

    ims = []
    for i in df_history['timestamp']:
        image_path = 'data/images/' + i + '.jpg'
        try:
            im = img_to_base64(image_path)
            ims.append(im)
        except:
            ims.append(image_path)
    df_history['image'] = ims
    st.data_editor(
        df_history,
        column_config={
            "image": st.column_config.ImageColumn(
                "Preview Image", help="Streamlit app preview screenshots"
            )
        },
        hide_index=True,
    )
    
# status
elif input_text == BARCODE_STATUS:
    st.title('สถานภาพปัจจุบัน')
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f'อาวุธในคลัง {len(rifles_in)} กระบอก')
        st.write(df_rifle[df_rifle['instock'] == True])
    with col2:
        st.subheader(f'อาวุธนอกคลัง {len(rifles_out)} กระบอก')
        st.write(df_rifle[df_rifle['instock'] == False])

# reset 
elif input_text == BARCODE_RESET:
    df_rifle['instock'] = True
    df_rifle.to_csv(RIFLE_DATA_PATH, index=False)
    st.title('reset complete!!')

# main
else:
    # head status
    st.title('ระบบเบิกจ่ายอาวุธอัตโนมัติ')
    col1, col2, col3 = st.columns(3)
    col1.subheader(f':blue[สถานะอาวุธในคลัง]')
    col1.header(f':blue[{len(rifles_in)} กระบอก]')
    col2.subheader(f':red[สถานะอาวุธนอกคลัง]')
    col2.header(f':red[{len(rifles_out)} กระบอก]')
    col3.subheader(f'รวม')
    col3.header(f'{len(rifles_in) + len(rifles_out)} กระบอก')

    st.markdown("""---""")

    # current rifle person id
    col11, col22 = st.columns(2)
    with col11:
        st.subheader(':green[อาวุธ]')
        if st.session_state.current_rifle:
            st.title(f":red[{st.session_state.current_rifle['rifle_id']}]")
            rifle_respon_id = st.session_state.current_rifle['person_id']
            try:
                rifle_respon_name = df_person[df_person['person_id']==rifle_respon_id].iloc[0]['name']
            except:
                rifle_respon_name = 'ไม่ปรากฎชื่อผู้รับผิดชอบ'
            st.write(f"{rifle_respon_name} ({rifle_respon_id})")

        else:
            st.write('--')
    with col22:
        st.subheader(':green[ผู้เบิก]')
        if st.session_state.current_person:
            st.title(f":red[{st.session_state.current_person['name']}]")
    
        else:
            st.write('--')

    st.markdown("""---""")

    #show current status text
    sta = 'โปรดแสกนอาวุธ และบัตรประจำตัว'
    if st.session_state.current_rifle and st.session_state.current_person:
        sta = 'สำเร็จ!!'
    elif st.session_state.current_rifle:
        sta = 'โปรดแสกนบัตรประจำตัว'
    elif st.session_state.current_person:
        sta = 'โปรดแสกนอาวุธ'

    example('#ff6320','#eaff2f','#000000',sta)

    # show history of rifle id
    if df_history_current_rifle_barcode.shape[0] != 0:

        ims = []
        for i in df_history_current_rifle_barcode['timestamp']:
            image_path = 'data/images/' + i + '.jpg'
            try:
                im = img_to_base64(image_path)
                ims.append(im)
            except:
                ims.append(image_path)
        df_history_current_rifle_barcode['image'] = ims
        st.data_editor(
            df_history_current_rifle_barcode,
            column_config={
                "image": st.column_config.ImageColumn(
                    "Preview Image", help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
        )


    # complete state
    if st.session_state.current_rifle and st.session_state.current_person:
        isin = toggle_instock(st.session_state.current_rifle['rifle_barcode'])
        if isin == 'True':
            action = 'in'
        else:
            action = 'out'

        #save data to csv
        data = {
            'rifle_barcode' : st.session_state.current_rifle['rifle_barcode'],
            'rifle_respon_name' : rifle_respon_name,
            'rifle_respon_id' : rifle_respon_id,
            'person_id' : st.session_state.current_person['person_id'],
            'person_barcode' : st.session_state.current_person['person_barcode'],
            'person_name' : st.session_state.current_person['name'],
            'timestamp' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action' : action
        }

        file_path = 'data/data_history.csv'
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(data.keys())  # Write the header row
            writer.writerow(data.values())

        # if st.button("Foo"):
        st.session_state.current_rifle = ''
        st.session_state.current_person = ''
        st.session_state.history_current_rifle_barcode = ''
        st.session_state.input_text = ''

        #capture image
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            exit()
        ret, frame = cap.read()
        if ret:
            directory = 'data/images'
            if not os.path.exists(directory):
                os.makedirs(directory)
            cv2.imwrite(f"{directory}/{data['timestamp']}.jpg", frame)
        cap.release()

        #voice
        pygame.mixer.init()
        if action == 'in':
            pygame.mixer.music.load("data/voices/in.mp3")
        else:
            pygame.mixer.music.load("data/voices/out.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
                

        # time.sleep(3)

        st.rerun()







