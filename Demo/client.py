import os

import openai
import requests
from openai import AzureOpenAI

openai.api_type = "azure"
# Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
openai.api_version = "2023-08-01-preview"

# Azure OpenAI setup
openai.api_base = "https://testing1310.openai.azure.com/"  # Add your endpoint here
openai.api_key = os.getenv("OPENAI_API_KEY")  # Add your OpenAI API key here
# deployment_id = "testing0613"  # Add your deployment ID here

# Azure AI Search setup
search_endpoint = "https://testingsearch1310.search.windows.net"  # Add your Azure AI Search endpoint here
search_key = os.getenv("SEARCH_KEY")  # Add your Azure AI Search admin key here
search_index_name = "paisa-bazar-credit-cards-index"  # Add your Azure AI Search index name here


def setup_byod(deployment_id: str) -> None:
    """Sets up the OpenAI Python SDK to use your own data for the chat endpoint.

    :param deployment_id: The deployment ID for the model to use with your own data.

    To remove this configuration, simply set openai.requestssession to None.
    """

    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):

        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    # Mount a custom adapter which will use the extensions endpoint for any call using the given `deployment_id`
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter()
    )

    openai.requestssession = session


# client = AzureOpenAI(
#     azure_endpoint='https://testing1310.openai.azure.com/',
#     api_version='2023-08-01-preview',
#     api_key=os.environ['OPENAI_API_KEY']
# )

client = AzureOpenAI(
    base_url=f"https://testing1310.openai.azure.com/openai/deployments/testing0613/extensions",
    api_version='2023-08-01-preview',
    api_key=os.environ['OPENAI_API_KEY']
)


def get_response_from_client(model, messages):
    return client.chat.completions.create(
        # Replace with the actual genai name if it exists
        model=model,
        # Send all messages from current session
        messages=messages,
        # Controls randomness of response
        temperature=0.8,
        # Set a limit on the number of tokens per genai response
        max_tokens=2000,
        # Similar to temperature, this controls randomness but uses a different method
        top_p=0.95,
        # Reduce the chance of repeating a token proportionally based on how often it has appeared in the text so far
        frequency_penalty=0,
        # Reduce the chance of repeating any token that has appeared in the text at all so far
        presence_penalty=0,
        # Number of completions
        n=1,
        # Make the genai end its response at a desired point
        stop=None,
        extra_body={
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "indexName": search_index_name,
                        "key": search_key
                    }
                }
            ]
        }
    )

# def get_response_from_client(deployment_id, messages):
#     setup_byod(deployment_id)
#
#     return openai.ChatCompletion.create(
#         messages=messages,
#         deployment_id=deployment_id,
#         dataSources=[  # camelCase is intentional, as this is the format the API expects
#             {
#                 "type": "AzureCognitiveSearch",
#                 "parameters": {
#                     "endpoint": "'$search_endpoint'",
#                     "indexName": "'$search_index'",
#                     "semanticConfiguration": "default",
#                     "queryType": "simple",
#                     "fieldsMapping": {},
#                     "inScope": True,
#                     "roleInformation": "You are an AI assistant that helps people find information.",
#                     "filter": None,
#                     "strictness": 3,
#                     "topNDocuments": 5,
#                     "key": "'$search_key'"
#                 }
#             }
#         ],
#         enhancements=undefined,
#         temperature=0,
#         top_p=1,
#         max_tokens=800,
#         stop=None,
#         stream=True
#     )
