import React, {useState} from "react";
import heal from '../assets/hands-holding.webp'


function Home(){

    const[username, setUserName] = useState('');
    const[password, setPassword] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        window.location.href = '/chat'
    }

    return(
      <div className='flex flex-grow overflow-auto w-full h-screen'>
        <div className="w-1/2 items-center justify-center hidden md:flex p-4">
            <img className="h-full w-full object-cover rounded-xl" src={heal} alt="Us"/>
        </div>
        <div className="md:w-1/2 w-full my-20">
            <div className="w-4/6 mx-auto">
            <p className="font-bold text-2xl pb-6">Welcome Back 👋</p>
            <p className="pb-10">Today is a great day, Let's share your concers here.</p>
                <form onSubmit={handleSubmit}>
                    <label forHtml="username" className="inline-block pb-2 text-xs">Username</label>
                    <input 
                        type="email" 
                        name="username" 
                        className="border border-border-grey bg-box-grey rounded-lg p-2 w-full focus:outline-none focus:border-none focus:ring-1 focus:ring-secondary"
                        placeholder="example@mail.com"
                        value={username}
                        onChange={(e) => setUserName(e.target.value)}
                        required
                    />
                    <label forHtml="password" className="inline-block pt-4 pb-2 text-xs">Password</label>
                    <input 
                        type="password" 
                        name="password" 
                        value={password}
                        className="border border-border-grey bg-box-grey rounded-lg p-2 w-full focus:outline-none focus:border-none focus:ring-1 focus:ring-secondary"
                        placeholder="Atleast 6 Characters"
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <div>
                        <input type="submit" value="Login" 
                            className="mt-6 py-2 px-6 rounded-lg bg-secondary text-white hover:bg-primary hover:shadow-md cursor-pointer"
                        />
                    </div>
                </form>
                <div className="mx-auto mt-6 w-full h-[0.1px] bg-border-grey">
                </div>
                <div className="w-full mt-2">
                    <p className="text-center text-xs pb-1">Not yet a user?</p>
                    <a href="/signup" className="block text-third hover:text-secondary text-center">Sign Up</a>
                </div>
            </div>
        </div>
      </div>
    )
  }

  export default Home;