import os
import uuid
from queue import Queue
from threading import Thread, Lock
from flask import Flask, request, jsonify, g
from psycopg2 import pool, OperationalError
import requests
import pyautogui
import subprocess

app = Flask(__name__)
request_queue = Queue()
itunes_lock = Lock()

db_pool = pool.SimpleConnectionPool(1, 20, "<your-database-url>")

def execute_with_retry(cur, query, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            return True
        except OperationalError:
            if attempt == max_retries - 1:
                raise
            g.db_conn = db_pool.getconn()
            cur = g.db_conn.cursor()
    return False

def get_db():
    if not hasattr(g, 'db_conn'):
        g.db_conn = db_pool.getconn()
    return g.db_conn

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db_conn'):
        db_pool.putconn(g.db_conn)

def init_db():
    db = get_db()
    with db.cursor() as cur:
        execute_with_retry(cur, '''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL
            )
        ''')
    db.commit()

def process_requests():
    with app.app_context():
        while True:
            job_id, bundle_id = request_queue.get()
            try:
                db = get_db()
                with db.cursor() as cur:
                    execute_with_retry(cur, "UPDATE jobs SET status = 'processing' WHERE id = %s", (job_id,))
                db.commit()
                run_itunes_locked(bundle_id)
                with db.cursor() as cur:
                    execute_with_retry(cur, "UPDATE jobs SET status = 'completed' WHERE id = %s", (job_id,))
                db.commit()
            except Exception as e:
                with db.cursor() as cur:
                    execute_with_retry(cur, "UPDATE jobs SET status = %s WHERE id = %s", (f"error: {str(e)}", job_id))
                db.commit()
            finally:
                request_queue.task_done()

Thread(target=process_requests, daemon=True).start()

@app.route('/run', methods=['GET'])
def run_itunes():
    bundle_id = request.args.get('bundle_id', type=str)
    if not bundle_id:
        return jsonify({
            'status': 'error',
            'error': 'Bundle ID is required'
        }), 400
    
    response = requests.get(f'https://itunes.apple.com/lookup?bundleId={bundle_id}')
    
    if response.status_code != 200:
        return jsonify({
            'status': 'error',
            'error': f"Failed to look up app: {response.text}"
        }), 500
    
    app_data = response.json()
    
    if app_data['resultCount'] == 0:
        return jsonify({
            'status': 'error',
            'error': 'App not found on the App Store'
        }), 404
    
    job_id = str(uuid.uuid4())
    db = get_db()
    with db.cursor() as cur:
        execute_with_retry(cur, "INSERT INTO jobs (id, status) VALUES (%s, 'queued')", (job_id,))
    db.commit()
    request_queue.put((job_id, bundle_id))
    
    return jsonify({
        'status': 'success',
        'data': {
            'job_id': job_id
        }
    }), 202

@app.route('/status/<job_id>', methods=['GET'])
def check_status(job_id):
    db = get_db()
    with db.cursor() as cur:
        execute_with_retry(cur, "SELECT * FROM jobs WHERE id = %s", (job_id,))
        job = cur.fetchone()
    
    if not job:
        return jsonify({
            'status': 'error',
            'error': 'Job not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': {
            'job_id': job[0],
            'status': job[1]
        }
    })

def run_itunes_locked(bundle_id):
    with itunes_lock:
        # force use of ImageNotFoundException
        pyautogui.useImageNotFoundException()

        # delete downloads folders to keep space
        os.system('rmdir /s /q C:\\Users\\' + os.getlogin() + '\\Music\\iTunes\\iTunes Media\\Downloads')
        os.system('rmdir /s /q C:\\Users\\' + os.getlogin() + '\\Music\\iTunes\\iTunes Media\\Music')

        # Open iTunes
        itunes_process = subprocess.Popen("C:\\Program Files\\iTunes\\iTunes.exe")
        pid = itunes_process.pid

        pyautogui.sleep(5)

        # get appstore informations. use requests to get the informations
        response = requests.get('https://itunes.apple.com/lookup?bundleId=' + bundle_id)
        response.raise_for_status()

        # if the response is 200 and all good, parse it
        res_json = response.json()

        app_name = res_json.get('results')[0].get('trackName')
        genre_name = res_json.get('results')[0].get('primaryGenreName')
        developer_name = res_json.get('results')[0].get('artistName')

        # check if we are in the music section
        try:
            if pyautogui.locateOnScreen('imgs/music_section.png'):
                print('Music section found on the screen. Switching to Appstore section.')
                pyautogui.click(pyautogui.locateOnScreen('imgs/section_selector.png'))
                pyautogui.click(pyautogui.locateOnScreen('imgs/apps_section.png'))
                pyautogui.sleep(3)
                if pyautogui.locateOnScreen('imgs/appstore_section_unselected.png'):
                    pyautogui.click(pyautogui.locateOnScreen('imgs/appstore_section_unselected.png'))
                    pyautogui.sleep(3)
        except:
            print('Music section not found on the screen. Continuing...')

        # Get on the iphone appstore section
        try:
            iphone_button = pyautogui.locateOnScreen('imgs/iPhone_button_selected.png')
            print("iPhone button found on the screen.")
        except pyautogui.ImageNotFoundException:
            print('Appstore not selected, selecting iphone section')
            try:
                iphone_button = pyautogui.locateOnScreen('imgs/iPhone_button_unselected.png')
                print("iPhone button found on the screen.")
                pyautogui.click(iphone_button)
            except pyautogui.ImageNotFoundException:
                print('iPhone button not found on the screen.')

        #click on the search bar
        try:
            search_bar = pyautogui.locateOnScreen('imgs/searchv2.png')
            pyautogui.click(search_bar)
            print('Search bar found on the screen.')
        except pyautogui.ImageNotFoundException:
            print('Search bar not found on the screen. Exiting...')
            raise Exception('Search bar not found')

        #type in the search bar
        try:
            pyautogui.write(app_name + ' ' + developer_name)
            pyautogui.sleep(2)
            pyautogui.press('enter')
            print(app_name + ' written in the search bar.')
        except:
            print('Error writing in the search bar. Exiting...')
            raise Exception('Error writing in search bar')

        pyautogui.sleep(5)

        # click get or download button while you find one on the screen ( keep clicking them until you dont find any )
        buttons_found = 0
        dl_buttons_found = 0

        while True:
            try:
                button = pyautogui.locateOnScreen('imgs/get_button_2.png')
                if not button:
                    break
                pyautogui.click(button)
                buttons_found += 1
                print('Get button found on the screen.')
                pyautogui.sleep(3)
            except Exception as e:
                print('no get button found on the screen.')
                break

        while True:
            try:
                if dl_buttons_found > 5:
                    break
                button = pyautogui.locateOnScreen('imgs/download_button.png')
                if not button:
                    break
                pyautogui.moveTo(button)
                dl_buttons_found += 1
                print('Download button found on the screen.')
            except Exception as e:
                print('no download button found on the screen.')
                break

        print('All possible apps were purchased.')

        if buttons_found == 0 and dl_buttons_found == 0:
            print("no buttons found. Exiting...")
            os.system('taskkill /f /pid ' + str(pid))
            raise Exception('No buttons found')
        
        print("we found " + str(buttons_found + dl_buttons_found) + " buttons. Finishing...")
        os.system('taskkill /f /pid ' + str(pid))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
