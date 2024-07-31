import json
import os 
from groq import Groq
from dotenv import load_dotenv
from google.cloud import storage

# Configuring environment
load_dotenv()

bucket_name='tx_explain'

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

def get_simData (network, tx_hash):
    sim_blob = bucket.blob(f'{network}/transactions/simulations/trimmed/{tx_hash}.json')
    if sim_blob.exists():
        cached_sim_data = json.loads(sim_blob.download_as_string()) 
        return cached_sim_data
    else:
        print('Simulation not in buckets.')
        return None

def get_explanationData (tx_hash):
    expl_blob = bucket.blob(f'ethereum/transactions/explanations/{tx_hash}.json')
    if expl_blob.exists():
        cached_expl_data = json.loads(expl_blob.download_as_string())['result']
        return cached_expl_data
    else:
        print('Explanation not in buckets.')
        return None
    
def assets_data (cached_sim_data):
    asset_amounts = [x['amount'] for x in cached_sim_data['asset_changes']]
    asset_names = [x['token_info']['name'] for x in cached_sim_data['asset_changes']]
    asset_symbols = [x['token_info']['symbol'] for x in cached_sim_data['asset_changes']]
    #asset_decimals = [x['token_info']['decimals']  for x in cached_sim_data['asset_changes']]

    assets = [
        {
            "amount": amount,
            "name": name,
            "symbol": symbol
        }
        for amount, name, symbol in zip(asset_amounts, asset_names, asset_symbols)
    ]

    assets_json = json.dumps(assets, indent=4)

    return  assets_json


def run_model (prompt, model = 'llama3-70b-8192'):

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_API_KEY,)

    try:
        chat_completion = groq_client.chat.completions.create(
            model= model, 
            messages=[{"role": "user", "content": prompt}]
        )
        return chat_completion
    except Exception as e:
        print("Error at run_model: ", e)

def correct_summary (cached_sim_data, cached_expl_data):
    assets_json = assets_data (cached_sim_data)

    prompt = f"""You will be provided with a transaction summary and a JSON object containing data about asset changes, including token names, symbols, and amounts.

                The transaction summary may contain incorrect numbers and decimal places for certain amounts. Your task is to use the asset changes JSON object to correct any wrong values in the transaction summary and return the corrected summary.

                Follow these steps to ensure accuracy:
                    1. Compare every token amount present in the summary with the amounts in the asset changes JSON object.
                    2. Pay close attention to the number of decimal places and the correct amount for each token.
                    3. Correct any discrepancies in the amounts in the summary based on the asset changes JSON object.
                    4. Ensure that no wrong amounts are left uncorrected. 

                When returning the corrected summary, do not return anything except the corrected text. 
                This also excludes any other comments, such as 'Here is the corrected summary:', 'Here is the corrected transaction summary:' and the like.
                The final output should contain nothing else except the corrected original summary.
        
                Original summary: \n{cached_expl_data}
                Asset changes json object: \n{assets_json}"""
    
    raw_result = run_model(prompt)
    modified_expl_data = raw_result.choices[0].message.content

    return modified_expl_data




tx_hash = '0x090e79fd0c0c2cbd1d5573310a58f0cff93a14c9a1d035e31ab1be8a7eeae58c'
network = 'arbitrum'

cached_sim_data = get_simData (network, tx_hash)
cached_expl_data = get_explanationData (tx_hash)

import time
start_time = time.time()

modified_expl_data = correct_summary(cached_sim_data, cached_expl_data)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Time taken to run the function: {elapsed_time:.2f} seconds")

print("\n")
print("Original Explanation String:")
print(cached_expl_data)
print("\n")
print("Modified Explanation String:")
print(modified_expl_data)
