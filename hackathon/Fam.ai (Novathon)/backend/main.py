import nest_asyncio
from starlette.staticfiles import StaticFiles
from blockchain.api import bchain_router
from chats.api import chats_router
from server import app
from docs.api import doc_router
from users.api import user_router
from pyngrok import ngrok

app.include_router(user_router)
app.include_router(doc_router)
app.include_router(chats_router)
app.include_router(bchain_router)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

try:
    auth_token = "2pVo1Jfcx0mc61PMALqsa8rgALwjyxoc"
    ngrok.set_auth_token(auth_token)
    ngrok_tunnel = ngrok.connect(8000, hostname='thoroughly-lasting-ladybug.ngrok-free.app')
    print('Public URL:', ngrok_tunnel.public_url)
    nest_asyncio.apply()
except:
    print("Ngrok error replace auth token and change url in frontend as well")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
