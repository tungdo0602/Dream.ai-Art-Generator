import requests
import time
from urllib.parse import urlparse, unquote
import os
import webbrowser
import base64

apiKey = "AIzaSyDCvp5MTJLUdtBYEKYWXJrlLzu1zuKM6Xw" # Get from "x-goog-api-key" header in "installations" requests
styles = {
        "default": 3,
        "paint": 50,
        "hdr": 52,
        "polygon": 49,
        "gouache": 48,
        "realistic": 32,
        "comic": 45,
        "line-art": 47,
        "malevolent": 40,
        "meme": 44,
        "throwback": 35,
        "ghibli": 22,
        "melancholic": 28,
        "provenance": 17,
        "darkfantasy": 10,
        "fantasy": 5,
        "mystical": 11,
        "hd": 7,
        "synthwave": 1,
        "vibrant": 6,
        "blacklight": 20        
    }

def cls():
    os.system("cls" if os.name == "nt" else "clear")

def downloadFile(url):
    return open(unquote(urlparse(url).path.split("/")[-1]), "wb").write(requests.get(url).content)

def createToken():
    global apiKey
    s = requests.Session()
    r = s.post("https://firebaseinstallations.googleapis.com/v1/projects/paint-prod/installations", headers={"Content-Type": "application/json", "x-goog-api-key": apiKey}, json={
        "appId": "1:181681569359:web:277133b57fecf57af0f43a",
        "authVersion": "FIS_v2",
        "sdkVersion": "w:0.5.1",
    })
    r2 = s.post("https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}".format(apiKey))
    return r2.json() if r.status_code == 200 else r.status_code

def createTask(token):
    r = requests.post("https://paint.api.wombo.ai/api/tasks", headers={"authorization": "bearer " + str(token), "Content-Type": "text/plain;charset=UTF-8"}, json={"premium": False})
    return r.json() if r.status_code == 200 else r.status_code

def createArt(token, id, options={"display_freq": 10, "prompt": "example", "style": 3}):
    r = requests.put("https://paint.api.wombo.ai/api/tasks/{}".format(id), headers={"authorization": "bearer " + str(token), "Content-Type": "text/plain;charset=UTF-8"}, json={
        "input_spec": options
    })
    return r
    
def main():
    global styles
    desc = input("Prompt: ")
    style = input("""
Style: default, paint, hdr, polygon, gouache, realistic, comic, line-art, malevolent, meme, throwback, ghibli, melancholic, provenance, darkfantasy, fantasy, mystical, hd, synthwave, vibrant, blacklight
>>> """)
    token = createToken()['idToken']
    task = createTask(token)
    id = task['id']
    print("Pending")
    createArt(token, id, {"display_freq": 10, "prompt": desc, "style": styles[style.lower()]})
    def fetchState(token, id):
        r = requests.get("https://paint.api.wombo.ai/api/tasks/{}".format(id), headers={"authorization": "bearer " + str(token)})
        return r
    while True:
        res = fetchState(token, id)
        if "completed" in res.json()['state']:
            cls()
            print("Result ({}): ".format(desc) + res.json()['result']['final'])
            if input("Get Image as Base64? [Y/N]: ").lower() == "y":
                bfile = base64.b64encode(requests.get(res.json()['result']['final']).content).decode("utf-8")
                name = unquote(urlparse(res.json()['result']['final']).path.split("/")[-1])
                open(name + ".txt", "w").write("data:image/{};base64,".format(os.path.splitext(name)[1].replace(".", "")) + bfile)
                print("Done!")
            if input("Download File? [Y/N]: ").lower() == "y":
                downloadFile(res.json()['result']['final'])
                print("Done!")
                return
            else:
                return
        else:
            print(res.json()['state'])
            time.sleep(1) # Avoid Rate Limit
            
if __name__ == "__main__":
    main()
