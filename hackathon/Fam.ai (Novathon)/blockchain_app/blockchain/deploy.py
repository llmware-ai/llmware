# import json
# import uvicorn
# from brownie import FundMe, SimpleCollectible, network, config, accounts
# from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware




# def get_account():
#     if network.show_active() == "development":
#         return accounts[0]
#     return accounts.add(config["wallets"]["from_key"])


# def main():
#     address = get_account()
#     print(address, type(address))
#     simple_collectable = SimpleCollectible.deploy({"from": address})
#     return FundMe, simple_collectable, address


# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow access from any origin
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["Authorization", "Content-Type"],
# )


# @app.get("/pay")
# def payment(url: str, name: str, description: str, result: str, confidense: int, to_address: str):
#     uri = {
#         "name": f"{name}",
#         "description": f"{description}",
#         "image": f"{url}",
#         "attributes": [
#             {
#                 "Result": f"{result}",
#                 "value": str(confidense)
#             }
#         ]
#     }
#     json_uri = json.dumps(uri)
#     # fund_me = FundMe[-1]
#     # tx = fund_me.fund({"from": address, "value": 30000000000000})
#     tx = simple_collectable.createCollectible(json_uri, to_address, {"from": address})
#     print(
#         f"You can view your nft at {OPENSEA_URL.format(simple_collectable.address, simple_collectable.tokenCounter() - 1)}")
#     # tx = fund_me.withdraw({"from": address})
#     print("Payment Transfered")


# def main():
#     uvicorn.run(app, port=8000, host="0.0.0.0")
# # def main():
# #     return FundMe, simple_collectable









import os
import json
import dotenv
import datetime
from PIL import Image
from web3 import Web3
from fastapi import APIRouter
from pydantic import BaseModel
from utils import file_to_sha256
from brownie.project import get_loaded_projects
from brownie.network.account import LocalAccount
from brownie import project, network, accounts, Contract
from concurrent.futures import ThreadPoolExecutor, as_completed

dotenv.load_dotenv()
bchain_router = APIRouter(tags=['bchain'])

p = project.load('blockchain')
network.connect('polygon')

SimpleCollectible = p.SimpleCollectible
get_loaded_projects()[0].load_config()
print(get_loaded_projects()[0])

def get_account() -> LocalAccount:
    return accounts.add(os.environ.get('PRIVATE_KEY'))


account = get_account()
print(account)


def get_or_deploy_contract():
    # simple_collectible = SimpleCollectible.deploy({"from": account, "gas_price": Web3.to_wei("3", "gwei")})
    deploy_file = 'deployed_address.txt'
    if os.path.exists(deploy_file):
        with open(deploy_file, 'r') as f:
            contract_address = f.read().strip()
        print(f"Loading existing contract at {contract_address}")
        return Contract.from_abi("SimpleCollectible", contract_address, SimpleCollectible.abi)
    else:
        print("Deploying new contract")
        contract = SimpleCollectible.deploy({"from": account, "gas_price": Web3.to_wei("4", "gwei")})
        with open(deploy_file, 'w') as f:
            f.write(contract.address)
        return contract


simple_collectible = get_or_deploy_contract()
account = get_account()


class PostData(BaseModel):
    user_address: str
    file_uid: str
    transction_id: str = 'xxx'


nft_url = "https://cardona-zkevm.polygonscan.com/nft/{}/{}"


@bchain_router.post('/mint_certificate')
async def mint_certificate(post_data: PostData):
    file_hash = file_to_sha256(f'assets/{post_data.file_uid}')
    client_address = post_data.user_address
    image_url = ""
    uri = {
        "name": f"Deep Fake Certification",
        "description": f"Deep Fake Certification",
        "image": image_url,
        "file_hash": file_hash,
        "attributes": [
            ""
        ]
    }
    json_uri = json.dumps(uri)
    tx = simple_collectible.createCollectible(json_uri, client_address,
                                              {"from": account, "gas_price": Web3.to_wei("4", "gwei")})

    tx.wait(1)
    token_id = simple_collectible.tokenCounter() - 1
    uri = simple_collectible.tokenURI(token_id)

    nft_url_formatted = nft_url.format(simple_collectible.address, token_id)

    return {
        "polygon_url": nft_url_formatted,
        'certificate_url': image_url,
        'token_id': token_id,
        'token_uri': uri
    }


@bchain_router.get('/cert/{user_address}')
async def get_user_nfts(user_address: str):
    try:
        user_address = Web3.to_checksum_address(user_address)
        total_supply = simple_collectible.tokenCounter()

        def check_and_get_nft(token_id):
            if simple_collectible.ownerOf(token_id) == user_address:
                uri = simple_collectible.tokenURI(token_id)
                polygon_url = nft_url.format(simple_collectible.address, token_id)
                return {
                    "token_id": token_id,
                    "uri": json.loads(uri),
                    "polygon_url": polygon_url
                }
            return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_and_get_nft, token_id) for token_id in range(total_supply)]
            user_nfts = [nft for nft in (future.result() for future in as_completed(futures)) if nft]

        return {"user_address": user_address, "nfts": user_nfts}
    except Exception as e:
        return {"error": f"Error getting user NFTs: {str(e)}"}


@bchain_router.get('/get_token_uri/{token_id}')
async def get_token_uri(token_id: int):
    try:
        if not simple_collectible:
            return {"error": "Contract not deployed"}
        uri = simple_collectible.tokenURI(token_id)
        return {"token_id": token_id, "uri": json.loads(uri)}
    except Exception as e:
        return {"error": f"Error getting tokenURI: {str(e)}"}
    
    