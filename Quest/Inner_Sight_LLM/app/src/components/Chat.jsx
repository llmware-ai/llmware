import { useState, useEffect } from "react"
import makeQuery from "../utils/request";
import './chat.css';


export default function Chat(){
    const [started, setStarted] = useState(false);
    const [query, setQuery] = useState("");
    const [chats, setChats] = useState([]);


    function initializeChat(){
        if(!started)
            setStarted(true)
    }

    function changeInput(e){
        setQuery(e.target.value)
    }
    function autoFill(e){
        setQuery(e.target.innerText)
    }
    
    async function submitQuery(){
        initializeChat()
        setChats((oldChats)=>{
            const newChats = [...oldChats]
            newChats.push({
                data: query,
                tag: "user"
            })
            return newChats
        })
        const response = await makeQuery(query)
        setChats((oldChats)=>{
            const newChats = [...oldChats]
            newChats.push({
                data: response.response,
                tag: "bot"
            })
            return newChats
        })
    }


    const Caption = () =>{
        return (
            <div id='captions'>
                <div id='caption-head'> Inner Sight:  Get Started! </div>
                <div id='caption-body'> 
                    Tell me about something thats on your mind <br /> <br />
                    Here are some things to pick from: <br />
                </div>
                <div id='options-container'> 
                    <div className="caption-box" onClick={autoFill}> How do I deal with Anxiety? </div>
                    <div className="caption-box" onClick={autoFill}> What are Some Signs of Depression? </div> 
                    <div className="caption-box" onClick={autoFill}> I've been Overthinking too much, what could be the reason? </div>
                </div>
            </div>
        )
    }

    const Chats = ({ chats }) =>{
        return (
            <div id='chats-container'>
            {
                chats.map((chat, i) => (
                    <div key={i}>
                        {chat.tag === 'user' ? (
                            <div className="user-chat chat">
                                <b>You</b> <br />
                                {chat.data}
                            </div>
                        ) : (
                            <div className="bot-chat chat">
                                <b>AI</b> <br />
                                {chat.data}
                            </div>
                        )}
                    </div>
                ))
            }
            </div>
        )
    }

    return (
        <div>
            <div id='chat-container'>
                {   
                    (!started) ? <Caption /> : <Chats chats={chats}/>
                }
            </div>

            <div id='message-box' className='container'>
                <div className='row'>
                    <div className='col-4'>
                        <input placeholder="Write about something that's going on your mind.." 
                            id='message-input' 
                            onChange={changeInput} 
                            value={query}
                        />
                        <button id='query-button' onClick={submitQuery}> Send </button>
                    </div>
                </div>
            </div>
        </div>
    )
}