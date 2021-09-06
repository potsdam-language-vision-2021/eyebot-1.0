# start slurk

conda create --name slurk python=3.7 -y
conda create --name oscar python=3.7 -y

# start ade http server
nohup python3 -m http.server 8080 -d /data/ImageCorpora/ADE20K_2016_07_26/images > image_host.out &

# start rasa
pushd eyebot_dm
nohup rasa run --enable-api &
popd

# start image_api
conda activate oscar
pushd image_server
> image_server.out
nohup python image_server/api.py api_extra.db > image_server.out &
conda deactivate
popd image_server

# start slurk
pushd slurk
conda activate slurk
SECRET_KEY=100 PORT=8070 nohup python local_run.py >> slurk_output.out &
conda deactivate
popd

# setup game
pushd clp-sose21-pm-vision/
nohup python ./avatar/scripts/slurk/game_setup_cli.py --token 00000000-0000-0000-0000-000000000000 --slurk_port 8070 > game_setup.out &

# these are the tokens from inspecting game_setup.out
cat <<EOF
Master token:  e32d3dd3-a96b-4f63-8f68-3e31ee36ac2c
Player token:  98d6de0f-3229-4128-a911-afe40fbe6a98
Avatar token:  8b4ce007-a65a-441d-bd44-739d3dc0c3de
EOF

# start master

> game_master.out
nohup python ./avatar/scripts/slurk/game_master_cli.py \
    --token 6311d646-defc-473d-be45-5b30c4f396d4 \
    --slurk_port 8070 > game_master.out &

# start avatar

> game_avatar.out
python setup.py install
nohup python avatar/scripts/slurk/game_avatar_cli.py \
    --token a173c18f-1b44-4b7e-8c12-9238f370ad11 \
    --slurk_port 8070 > game_avatar.out &


# start avatar
./ngrok http --region=us --hostname=eyebot.ngrok.io 8070