import { useState } from 'react'
import logo from "./assets/innersightlogo.png";
import './App.css'
import Chat from './components/Chat'
import "animate.css";


function App() {
  const [chatMode, setchatMode] = useState(false);

  function startChat(){
    setchatMode(true);
  }


  const AppComponent = (chatMode) ? <Chat /> : (
    <div id='app-container' className="container animate__animated animate__fadeInDownBig">
      <div className="row">
        <div className='col-3'>
          <img src={logo} id='app-logo'/>
        </div>
      </div>

      <div className='row' id='app-caption'>
          <div id="caption-head"> 
              Inner Sight: Your Personal <br /> Conversational AI Therapist! <br />
          </div> <br />
          <div id='caption-body'>
            Experience the conversational experience to talk about things you can't share with most. <br />
            Inner Sights provides you insights on yourself, <br /> Similar to a traditional therapy <br />
          </div>
      </div>

      <div>
        <button id='start-btn' onClick={startChat}> Get Started </button>
      </div>
      
    </div>
  )

  return AppComponent;
}

export default App
