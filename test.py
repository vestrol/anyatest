import streamlit as st 
import cv2
import AnalyzerModule as pm
import numpy as np
import mediapipe as mp
import tempfile
import os
import time
import base64
from io import BytesIO
from streamlit_extras.stylable_container import stylable_container
import matplotlib.pyplot as plt
from ffmpy import FFmpeg
import streamlit_analytics


joints = [pm.SHOULDER_RIGHT,pm.HIP_RIGHT,pm.KNEE_RIGHT,pm.ANKLE_RIGHT,pm.ELBOW_RIGHT]
limbs = [pm.ARM_LOWER_RIGHT,pm.ARM_UPPER_RIGHT,pm.UPPER_BODY_RIGHT,pm.LEG_UPPER_RIGHT,pm.LEG_LOWER_RIGHT, pm.FOOT_RIGHT]

st.set_page_config(
    page_title="SWISH!",
    page_icon= "🏀",
    )

with streamlit_analytics.track():
    st.markdown('''
    <style>
    .css-k7vsyb.eqr7zpz1 #danger-zone
    {
        display: none;
    }
    .streamlit-expanderHeader.st-ae.st-by.st-ag.st-ah.st-ai.st-aj.st-bz.st-c0.st-c1.st-c2.st-c3.st-c4.st-c5.st-ar.st-as.st-b6.st-b5.st-b3.st-c6.st-c7.st-c8.st-b4.st-c9.st-ca.st-cb.st-cc.st-cd
    {
        display: none;
    }
    </style>
    ''', unsafe_allow_html=True)
    
    col = st.columns([0.1, 0.7, 0.1])
    with col[1]:   
        st.image("logo7.jpg")
    
    st.header("About")
    with st.container():
        st.markdown('''<p style="font-family:calibri; color:white;">
        <span style="color:white; font-size: 20px"> What? </span> <br> SWISH! is a prototype to analyse the posture of a basketball shot to achieve the most mechanically efficient shot. <br> <br> 
        <span style="color:white; font-size: 20px"> How? </span> <br> Using Matplotlib, the algorithm analyses the shoulder, hip, knee, ankle, elbow, and wrist. <br> <br> 
        <span style="color:white; font-size: 20px"> Result? </span> <br>
            - score<br>
            - feedback mechanism <br> 
            - visual representation of each body part’s relative activation and time to improve shooting posture </p>''', unsafe_allow_html=True)
    
    st.header("Instruction for video")
    with st.container():
        st.markdown('''
        1. Shot must be close to the camera
        2. background movement must be minimized
        3. Ensure your side profile is being captured 
        4. Try to get your whole body in the frame
        5. If the video is not converted; please shoot it again keeping the above in mind.
        ''')
    
    st.header("HOW TO?")
    st.markdown('''<p style="font-family:calibri; color:white;">
    <span style="color:red; font-size: 23px"> STEP 1. </span> <br> Record your video
    <br> <br> <span style="color:red; font-size: 23px; font-family:calibri"> STEP 2. </span> <br> Upload your video file </p>''', unsafe_allow_html=True)
    
    video = st.file_uploader('Uploader:')
    analyzer = pm.Analyzer()
    pl = st.empty()
    
    if video is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tfile:
                tfile.write(video.read())
                tfile_path = tfile.name
            
            # Using FFmpeg with in-memory files
            user_video_path = tempfile.NamedTemporaryFile(suffix='.mov').name
            ff = FFmpeg(inputs={tfile_path: None}, outputs={user_video_path: None})
            ff.run()
            st.write('Video Conversion Done')
            st.video(user_video_path)
            
            analyzer.analyze(user_video_path, joints)
            with pl:
                st.write("Your overall score:")
                st.write(analyzer.score_motion())
                st.write(analyzer.give_suggestions())
                
            st.write('The output video is being processed')
            col1, col2 = st.columns(2)
            col1.pyplot(analyzer.output_graph())
            
            analyzer.output_video(name='user', limbs=limbs, out_frame_rate=12)
            processed_video_path = tempfile.NamedTemporaryFile(suffix='.avi').name
            processed_mov_path = tempfile.NamedTemporaryFile(suffix='.mov').name
            
            fr = FFmpeg(inputs={processed_video_path: None}, outputs={processed_mov_path: None})
            fr.run()
            col2.video(processed_mov_path)
            
            time.sleep(2)
            
            with open(processed_video_path, "rb") as v:
                st.download_button("Download Processed Video", v, file_name="user.avi")
            
            with open("Graph.png", "rb") as v:
                st.download_button("Download Graph", v, file_name="Graph.png")
            
        except Exception as e:
            st.markdown(f"There is a problem with the video, please follow the instructions. Error: {str(e)}")

    st.markdown('''<p style="font-family:calibri; color:white;">
    <span style="color:red;font-size: 23px"> STEP 3. </span> <br> Wait for the process to run
    <br> <br> <span style="color:red;font-size: 23px"> STEP 4. </span> <br> Posture Reviewed!
    <br> <br> <span style="color:red; font-size: 23px; font-family:calibri"> STEP 5. </span> <br> You may download the analysed graph and video to record your performance :) </p>''', unsafe_allow_html=True)
