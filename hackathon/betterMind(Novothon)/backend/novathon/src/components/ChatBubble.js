import React from 'react';

const ChatBubble = ( { message } ) => {
   

    return(
        <div className={`w-full my-4 flex justify-start items-center`}>
                <div 
                    className={`flex flex-col bg-primary p-2 text-secondary
                    w-4/6 rounded-xl break-normal hyphens-auto`}  
                >
                    <div className={`font-black text-third`}>
                        {message.name}
                    </div>
                    <div className='flex items-center overflow-hidden'>
                        {message.file ? 
                            <a href={message.file} target="blank">
                                <img src={message.file} 
                                    alt='Uploaded' 
                                    className='mx-2 h-56 rounded-xl'/>
                            </a> : 
                            <p className='mx-2'>{message.text}</p>}
                    </div>
                </div>
            </div>
    );
}

export default ChatBubble;