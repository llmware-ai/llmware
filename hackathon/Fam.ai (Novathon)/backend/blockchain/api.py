import os
import json
import dotenv
import datetime
from PIL import Image
from web3 import Web3
from fastapi import APIRouter
from pydantic import BaseModel
from brownie.project import get_loaded_projects
from brownie.network.account import LocalAccount
from brownie import project, network, accounts, Contract
from concurrent.futures import ThreadPoolExecutor, as_completed

from global_vars import Var

dotenv.load_dotenv()
bchain_router = APIRouter(tags=['bchain'])

p = project.load('blockchain')
chain = int(input("Enter chain \n1 Polygon\n2 Etherium\n3 Continue Without Blockchain\n\nEnter your Choice:"))
sepolia_nft = "https://sepolia.etherscan.io/nft/{}/{}"
polygon_nft = "https://cardona-zkevm.polygonscan.com/nft/{}/{}"

if chain == 1:
    network.connect('polygon')
    nft_url = polygon_nft
    deploy_file = 'polygon_deployed_address.txt'
elif chain == 2:
    network.connect('sepolia')
    nft_url = sepolia_nft
    deploy_file = 'sepolia_deployed_address.txt'
elif chain == 3:
    Var.use_blockchain = False
else:
    raise Exception("Invalid choice")

SimpleCollectible = p.SimpleCollectible
get_loaded_projects()[0].load_config()
print(get_loaded_projects()[0])


def get_account() -> LocalAccount:
    return accounts.add(os.environ.get('PRIVATE_KEY'))


account = get_account()
print(account)


def get_or_deploy_contract():
    # simple_collectible = SimpleCollectible.deploy({"from": account, "gas_price": Web3.to_wei("3", "gwei")})
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
    img_url: str
    desc: str


@bchain_router.post('/upload_to_blockchain')
async def mint_certificate(post_data: PostData):
    # file_hash = file_to_sha256(f'assets/{post_data.file_uid}')
    client_address = post_data.user_address
    uri = {
        "name": f"Deep Fake Certification",
        "description": post_data.desc,
        "image": post_data.img_url,
        # "file_hash": file_hash,
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
        'certificate_url': post_data.img_url,
        'token_id': token_id,
        'token_uri': uri
    }


@bchain_router.get('/get_uploaded_docs/{user_address}')
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


@bchain_router.get('/get_document_meta/{token_id}')
async def get_token_uri(token_id: int):
    try:
        if not simple_collectible:
            return {"error": "Contract not deployed"}
        uri = simple_collectible.tokenURI(token_id)
        return {"token_id": token_id, "uri": json.loads(uri)}
    except Exception as e:
        return {"error": f"Error getting tokenURI: {str(e)}"}
