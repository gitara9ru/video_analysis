from dataclasses import dataclass
import requests
from time import sleep
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()
AZURE_VIDEO_INDEXER_SUBSCRIPTION_KEY = os.environ.get('AZURE_VIDEO_INDEXER_SUBSCRIPTION_KEY')
AZURE_VIDEO_INDEXER_ACCOUNT_ID = os.environ.get('AZURE_VIDEO_INDEXER_ACCOUNT_ID')

IndexPreset = "Default"
# Create a class with attributes that relate to VideoIndexer credentials
@dataclass
class VideoIndexer:
    subscription_key: str = AZURE_VIDEO_INDEXER_SUBSCRIPTION_KEY
    account_id: str = AZURE_VIDEO_INDEXER_ACCOUNT_ID
    location: str = "TRIAL"  # change this if you have a paid subscription tied to a specific location
    # language = "Japanese"
    language = "ja-JP"

    @classmethod
    def get_access_token(cls):
        """
        Get an access token from the Video Indexer API. These expire every hour and are required in order to use the
        service.
        :return access_token: string.
        """

        url = "https://api.videoindexer.ai/Auth/{}/Accounts/{}/AccessToken?allowEdit=true".format(
            cls.location, cls.account_id
        )
        headers = {
            "Ocp-Apim-Subscription-Key": cls.subscription_key,
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            access_token = response.json()
            return access_token
        else:
            print("[*] Error when calling video indexer API.")
            print("[*] Response : {} {}".format(response.status_code, response.reason))


    @classmethod
    def send_to_video_indexer(cls, video_url, video_id, access_token):
        """
        Send a video to be analysed by video indexer.
        :param video_id: string, identifier for the video..
        :param video_url: string, public url for the video.
        :param access_token: string, required to use the API.
        :return video_indexer_id: string, used to access video details once indexing complete.
        """

        # Set request headers and url
        headers = {
            "Content-Type": "multipart/form-data",
            "Ocp-Apim-Subscription-Key": cls.subscription_key,
        }
        video_indexer_url_format = "https://api.videoindexer.ai/{}/Accounts/{}/Videos?name={}&privacy=Private&videoUrl={}&indexingPreset={}&accessToken={}&language={}&customLanguages={}&sendSuccessEmail=True&streamingPreset=NoStreaming"

        video_indexer_url = video_indexer_url_format.format(cls.location, cls.account_id, video_id, video_url, IndexPreset, access_token, cls.language, cls.language)

        # Make request and catch errors
        response = requests.post(url=video_indexer_url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            print(response_json)
            video_indexer_id = response_json["id"]
            return video_indexer_id
        # If the access token has expired get a new one
        if response.status_code == 401:
            print("[*] Access token has expired, retrying with new token.")
            access_token = cls.get_access_token()
            video_indexer_new_url = video_indexer_url_format.format(cls.location, cls.account_id, video_id, video_url, IndexPreset, access_token, cls.language, cls.language)
            response = requests.post(url=video_indexer_new_url, headers=headers)
            if response.status_code == 200:
                video_indexer_id = response.json()["id"]
                return video_indexer_id
            else:
                print("[*] Error after retrying.")
                print(
                    "[*] Response : {} {}".format(response.status_code, response.reason)
                )
        # If you are sending too many requests
        if response.status_code == 429:
            print("[*] Throttled for sending too many requests.")
            time_to_wait = response.headers["Retry-After"]
            print("[*] Retrying after {} seconds".format(time_to_wait))
            sleep(int(time_to_wait))
            response = requests.post(url=video_indexer_url, headers=headers)
            if response.status_code == 200:
                video_indexer_json_output = response.json()
                return video_indexer_json_output
            else:
                print("[*] Error after retrying following throttling.")
                print(
                    "[*] Response : {} {}".format(response.status_code, response.reason)
                )
        else:
            print("[*] Error when calling video indexer API.")
            print("[*] Response : {} {}".format(response.status_code, response.reason))


    @classmethod
    def get_indexed_video_data(cls, video_id, default_access_token):
        """
        Retrieves data on the video after analysis from the Video Indexer API.
        :param video_id: string, unique identifier for the indexed video.
        :param access_token: string, required to use the API.
        :return video_indexer_json_output: JSON, analysed video data.
        """

        # Set request headers and url
        headers = {
            "Ocp-Apim-Subscription-Key": cls.subscription_key
        }
        # language = "ja-JP"
        # url_format = "https://api.videoindexer.ai/{}/Accounts/{}/Videos/{}/Index?accessToken={}&language={}"
        # url = url_format.format(
        #     cls.location, cls.account_id, video_id, access_token, cls.language
        # )

        access_token = default_access_token


        while True:
            # Make request and handle unauthorized error
            url_format = "https://api.videoindexer.ai/{}/Accounts/{}/Videos/{}/Index?accessToken={}"
            url = url_format.format(
                cls.location, cls.account_id, video_id, access_token
            )
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                video_indexer_json_output = response.json()
                if video_indexer_json_output["state"] in ['Processed', 'Failed', 'Quarantined']:
                    return video_indexer_json_output

            # If the access token has expired get a new one
            elif response.status_code == 401:
                print("[*] Access token has expired, retrying with new token.")
                access_token = cls.get_access_token()
                url = url_format.format(
                    cls.location, cls.account_id, video_id, access_token
                )
                response = requests.get(url=url, headers=headers)
                if response.status_code == 200:
                    video_indexer_json_output = response.json()
                    if video_indexer_json_output["state"] in ['Processed', 'Failed', 'Quarantined']:
                        return video_indexer_json_output
                else:
                    print("[*] Error after retrying.")
                    print(
                        "[*] Response : {} {}".format(response.status_code, response.reason)
                    )
                    return
            else:
                print("[*] Error when calling video indexer API.")
                print("[*] Response : {} {}".format(response.status_code, response.reason))
                return
            sleep(10)


if __name__ == "__main__":
    vi = VideoIndexer()

    # To send videos
    my_access_token = vi.get_access_token()
    my_video_url = os.getenv('AZURE_VIDEO_INDEXER_BLO_URL')
    my_video_id = 'video_name'
    response_id = vi.send_to_video_indexer(
        video_url=my_video_url,
        video_id=my_video_id,
        access_token=my_access_token,
    )
    print(response_id)


    # To retrieve videos
    start = time.time()
    indexer_response = vi.get_indexed_video_data(
        video_id=response_id, default_access_token=my_access_token
    )
    end = time.time()
    print('time {}s'.format(end - start))
    if indexer_response["state"] == "Processed":
        with open("video_indexer_response_{}_{}.json".format(my_video_id, IndexPreset), "w") as f:
            json.dump(indexer_response, f, ensure_ascii=False)
    else:
        print("[*] Video has not finished processing")