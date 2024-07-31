# correct_decimals_llama3
Testing a simple function using llama3 model to correct decimals in the transaction summary.
The model is prompted to compare all token amounts in the summary with token amounts in the asset_changes, and then to correct them if there are any errors.

Input: Transaction summary, json file with correct amounts, token symbols and token names (extracted from asset_changes in sim_data)
Output: Transaction summary with corrected decimals

Note: Since it uses data in asset_changes, it assumes asset_changes is not empty / doesn't have null or "" values. 
In case of missing data, another function that fixes that must be applied first. 
We already have that function, but it has to be reintegrated into the tx_explain flow.

Requirements to run the file:
1. Google credentials .json file with access to buckets
2. Groq api key
