import React from 'react';
import { Button } from '@mui/material';

const SignInScreen = (props) => {
    const handleClick = () => {
        props.signIn();
    }
    return(
        <>
            <div className='flex-grow flex justify-center items-center'>
                <Button variant='contained' onClick={handleClick}>Sign In</Button>
            </div>
        </>
    );
}

export default SignInScreen;