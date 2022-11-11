# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_sentiment.py
DESCRIPTION:
    This sample demonstrates how to analyze sentiment in documents.
    An overall and per-sentence sentiment is returned.
    In this sample we will be a skydiving company going through reviews people have left for our company.
    We will extract the reviews that we are certain have a positive sentiment and post them onto our
    website to attract more divers.
USAGE:
    python sample_analyze_sentiment.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()
AZURE_LANGUAGE_KEY = os.environ.get('AZURE_LANGUAGE_KEY')
AZURE_LANGUAGE_ENDPOINT = os.environ.get('AZURE_LANGUAGE_ENDPOINT')


def sample_analyze_sentiment() -> None:
    print(
        "In this sample we will be combing through reviews customers have left about their"
        "experience using our skydiving company, Contoso."
    )
    print(
        "We start out with a list of reviews. Let us extract the reviews we are sure are "
        "positive, so we can display them on our website and get even more customers!"
    )

    # [START analyze_sentiment]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = AZURE_LANGUAGE_ENDPOINT
    key = AZURE_LANGUAGE_KEY

    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    documents = [
        {
            "text": 'ええ、今日は会議が多くて、とても疲れました。',
            "id": 1,
            "lang": 'jp'
        },
        {
            "text": '会議の内容も難しくてえ？知らない人ばっかりだったのでとても緊張しました。',
            "id": 2,
            "lang": 'jp'
        },
        {
            "text": '業務終わります。',
            "id": 3,
            "lang": 'jp'
        }
    ]

    result = text_analytics_client.analyze_sentiment(documents, show_opinion_mining=True)
    docs = [doc for doc in result if not doc.is_error]
    sentences = []
    for doc in docs:
        sentiment = doc["sentiment"]
        sntncs = doc["sentences"]
        sentence = list(map(lambda sntnc: {"sentiment": sntnc["sentiment"], "sentences": sntnc["text"]}, sntncs))
        sentences.append({"sentiment": sentiment, "sentences": sentence})

    with open("text_analyze_response_tukaremaru.json", "w") as f:
        json.dump(sentences, f, ensure_ascii=False)


if __name__ == '__main__':
    sample_analyze_sentiment()