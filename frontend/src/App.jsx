import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import { Upload } from 'lucide-react'
import UploadPanel from './components/UploadPanel.jsx'
import ChatWindow from './components/ChatWindow.jsx'

const App = () => {


  const[mode, setMode] = useState("chat")
  return (
    <div  className='relative flex flex-row items-start justify-start gap-3'>
      
     
      <Sidebar mode = {mode} setMode = {setMode} />
      <ChatWindow mode = {mode} />



    </div>
  )
}

export default App