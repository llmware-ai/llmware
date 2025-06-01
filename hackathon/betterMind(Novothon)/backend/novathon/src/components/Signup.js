import React, {} from "react";
import heart from '../assets/sunlight.jpg'


function Signup(){
    return(
      <div className='flex flex-grow w-full h-screen mb-4'>
        <div className="w-1/2 items-center justify-center p-4 overflow-hidden hidden md:flex">
            <img className="h-full w-full object-cover rounded-xl" src={heart} alt="Happy Thomas"/>
        </div>
        <div className="md:w-1/2 w-full my-20">
            <div className="w-4/6 mx-auto">
            <p className="font-bold text-2xl pb-6">Let's us help you👋</p>
            <p className="pb-10">You are not alone in this time of hardship. Hold our hands, it's always there for you.</p>
                <form>
                    <label forHtml="name" className="inline-block pb-2 text-xs">Name</label>
                    <input 
                        type="text" 
                        name="name" 
                        className="border border-border-grey bg-box-grey rounded-lg p-2 w-full focus:outline-none focus:border-none focus:ring-1 focus:ring-secondary"
                        placeholder="What should we call you?"
                    />
                    <label forHtml="username" className="inline-block pb-2 text-xs">Username</label>
                    <input 
                        type="text" 
                        name="username" 
                        className="border border-border-grey bg-box-grey rounded-lg p-2 w-full focus:outline-none focus:border-none focus:ring-1 focus:ring-secondary"
                        placeholder="example@mail.com"
                    />
                    <label htmlFor="gender" className="block py-2 text-xs font-medium text-gray-700">
                        Gender
                    </label>
                    <div className="flex items-center space-x-4">
                        {/* Male Option */}
                        <label className="flex items-center space-x-2">
                            <input 
                                type="radio" 
                                name="gender" 
                                value="male" 
                                className="form-radio text-blue-500 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">Male</span>
                        </label>
                        
                        {/* Female Option */}
                        <label className="flex items-center space-x-2">
                            <input 
                                type="radio" 
                                name="gender" 
                                value="female" 
                                className="form-radio text-blue-500 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">Female</span>
                        </label>
                        </div>
                    <label forHtml="age" className="block pt-4 pb-2 text-xs">Age</label>
                    <input 
                        type="number" 
                        name="age" 
                        className="border border-border-grey bg-box-grey rounded-lg p-2 w-full focus:outline-none focus:border-none focus:ring-1 focus:ring-secondary"
                        placeholder="We know you are always a kid!"
                    />
                    <label forHtml="password" className="inline-block pt-4 pb-2 text-xs">Password</label>
                    <input 
                        type="password" 
                        name="password" 
                        className="border border-border-grey bg-box-grey rounded-lg p-2 w-full focus:outline-none focus:border-none focus:ring-1 focus:ring-secondary"
                        placeholder="Atleast 6 Characters"
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
                    <p className="text-center text-xs pb-1">Our user?</p>
                    <a href="/" className="block text-third hover:text-secondary text-center">Sign In</a>
                </div>
            </div>
        </div>
      </div>
    )
  }

  export default Signup;