import axios from "axios";
const host = 'http://127.0.0.1:8000'


export default async function makeQuery(queryData){
    try{
        const response = await axios.get(`${host}/query/?query=${queryData}`)
        return response.data
    }
    catch(e){
        console.log(e)
    }
}