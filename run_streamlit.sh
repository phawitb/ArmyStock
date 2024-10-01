#!/bin/bash

sleep 5

source /home/phawit/anaconda3/etc/profile.d/conda.sh  # Adjust this path if necessary
conda activate rifle  # Replace 'your_env_name' with your actual environment name
cd /home/phawit/Documents/ArmyStock

streamlit run app.py --server.headless true --server.port 8509 &

sleep 5

chromium-browser --start-fullscreen http://localhost:8509

