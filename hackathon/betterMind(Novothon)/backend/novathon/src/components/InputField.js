import React, { useState } from 'react';

// import { auth, db, storage } from '../firebase';
// import { addDoc, collection, serverTimestamp } from 'firebase/firestore';
// import { getDownloadURL, ref, uploadBytes } from 'firebase/storage'

import { IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const InputField = ({scroll, sendMessage}) => {

    
    const[message, setMessage] = useState("");
    
    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() === "") return;
        // Send message to the parent component
        sendMessage(message);
        // Clear the input field
        setMessage("");
    };

    return(
        <div className='p-2 flex justify-between items-center 
            w-full'>
            
            <form className='flex w-full'
                onSubmit={handleSubmit}>
            <div className=' flex-grow mx-4 bg-box-grey border border-border-grey
                rounded-xl px-2 flex'>
                <input type='text' 
                    className=' bg-box-grey rounded-lg p-2 outline-none flex-grow'
                    placeholder='Type here...'
                    value={message}
                    onChange={(e) => {setMessage(e.target.value)}}
                />
                
            </div>
            <div className=''>
                <IconButton type='submit' sx={{padding: 1, background: '#D4D7E3'}}>
                    <SendIcon 
                        sx={{color: '#02182B'}} />
                </IconButton>
            </div>
            </form>
        </div>
    );
}

export default InputField;