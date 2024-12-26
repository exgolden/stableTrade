# stableTrade
## Setup initialization
1. Create a Python venv: `python3 -m venv venv` if you dont have venv, install it with: `pip3 install virtualenv`
2. Activate Python venv: `python 3 source venv/bin/activate`
3. Ensure youre using the correct Python with : `which python`, 
    it should retrieve something like: `<path_of_project>/stableTrade/venv/bin/Python`
4. Install the required dependencies with: `pip3 install -r .requirements.txt`

## API initialization
1. Create an API key and secret key from Settings>Account>API Management. 
    You will need to enable 2FA and whitelist your IP Adress to enable
    Spot & Margin trading.
2. Store your API key and Secret key in a .env file as:
   ```
    API_KEY=<api_key>
    SECRET_KEY=<secret_key>
   ``` 

