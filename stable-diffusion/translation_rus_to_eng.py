import requests
import json


def translate(text: str) -> str:
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"

    querystring = {"to[0]":"en","api-version":"3.0","from":"ru","profanityAction":"NoAction","textType":"plain"}

    payload = [{"Text": text}]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "9ddf5f355amsh007fe51f49dd5e8p147ba7jsn178984e3fded",
        "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    return json.loads(response.text)[0]['translations'][0]['text']
    

def main():
    sample_text = 'Санкт-Петербург - самый красивый город'
    print(translate(sample_text))

if __name__ == "__main__":
    main()







