import motor.motor_asyncio

from schemas import AccountData, ProfileData, DocData


class FamAIDataBase:
    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/')
        self.db = self._client["FamAIDataBase"]
        self.usrDB = self.db["usrDB"]
        self.prfDB = self.db["prfDB"]
        self.docDB = self.db["docDB"]

    async def create_user(self, user: AccountData):
        return await self.usrDB.insert_one(user.model_dump())

    async def get_user(self, address: str):
        return await self.usrDB.find_one({"address": address}, {'_id': 0})

    async def create_profile(self, profile_data: ProfileData):
        return await self.prfDB.insert_one(profile_data.model_dump())

    async def delete_profile(self, address: str, prfid: str):
        await self.prfDB.delete_one({'address': address, 'prfid': prfid})

    async def get_profile(self, address: str, prfid: str):
        return await self.prfDB.find_one({'address': address, 'prfid': prfid}, {'_id': 0})

    async def get_profiles(self, address: str):
        return await self.prfDB.find({'address': address}, {'_id': 0}).to_list(None)

    async def add_document(self, doc_data: DocData):
        return await self.docDB.insert_one(doc_data.model_dump())

    async def get_documents(self, address: str, prfid: str):
        return await self.docDB.find({'address': address, 'prfid': prfid}, {'_id': 0}).to_list(None)

    async def delete_document(self, address: str, prfid: str, filename: str):
        await self.docDB.delete_one({'address': address, 'prfid': prfid, 'filename': filename})