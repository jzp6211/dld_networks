from django.http import JsonResponse
import os
import json
import base64
import pandas as pd
import logging
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger('dld')

@csrf_exempt
def save_network_data(request):
    if request.method == 'POST':
        try:
            post_data = json.loads(request.body)
            # logger.info(f"Post data received: {post_data}")
            data = post_data.get('filedata', '')
            if len(data) > 0:
                user_id=data['trials'][0]['user_id']
                file_name = f"{user_id}_networks.csv"
                BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(os.path.join(BASE_PATH,"networks_data/"), file_name)
                df = pd.DataFrame(data['trials'])
                df.to_csv(file_path, index=False, na_rep='')

            return JsonResponse({"status": "success", "message": "Data saved!"})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


@csrf_exempt
def save_network_data_2(request):
    if request.method == 'POST':
        try:
            post_data = json.loads(request.body)
            # logger.info(f"Post data received: {post_data}")
            data = post_data.get('filedata', '')
            if len(data) > 0:
                user_id=data['trials'][0]['user_id']
                file_name = f"{user_id}_networks_2.csv"
                BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(os.path.join(BASE_PATH,"networks_data/"), file_name)
                df = pd.DataFrame(data['trials'])
                df.to_csv(file_path, index=False, na_rep='')

            return JsonResponse({"status": "success", "message": "Data saved!"})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

@csrf_exempt
def save_audio_response(request):
    if request.method == 'POST':
        post_data = json.loads(request.body)
        # logger.info(f"Post data received: {post_data}")
        data = post_data.get('filedata', '')
        if len(data) > 0:
            user_id=data['trials'][0]['user_id']
            file_name = f"{user_id}.csv"
            BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(os.path.join(BASE_PATH,"audio_data/"), file_name)

    for trial in data['trials']:
        if trial['trial_type'] == 'html-audio-response':
            b64_audio = trial.get('response', '')
            if b64_audio:
                audio_data = base64.b64decode(b64_audio)
                wav_file_name = f"audio_{trial['user_id']}_{trial['task']}_{trial['trial_index']}.wav"
                if not(os.path.isdir(f"{BASE_PATH}/{trial['user_id']}")):
                    os.mkdir(f"{BASE_PATH}/{trial['user_id']}")
                f = open(f"{BASE_PATH}/{trial['user_id']}/{wav_file_name}", 'wb')
                f.write(audio_data)
                f.close()
                return JsonResponse({"status": "success", "message": "Data saved!"})
            else:
                return JsonResponse({"status": "error", "message": "not audio"})
        else:
            return JsonResponse({"status": "success", "message": "wrong trial type"})

@csrf_exempt
def save_data(request):
    if request.method == 'POST':
        try:
            post_data = json.loads(request.body)
            # logger.info(f"Post data received: {post_data}")
            data = post_data.get('filedata', '')
            if len(data) > 0:
                user_id=data['trials'][0]['user_id']
                file_name = f"{user_id}.csv"
                BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(os.path.join(BASE_PATH,"audio_data/"), file_name)
                df = pd.DataFrame(data['trials'])
                df.to_csv(file_path, index=False, na_rep='')

            return JsonResponse({"status": "success", "message": "Data saved!"})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            logger.info(f"Request body: {request.body.decode('utf-8')}")
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)