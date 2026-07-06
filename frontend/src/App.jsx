import React from 'react'
import Sidebar from './components/Sidebar'
import { Upload } from 'lucide-react'
import UploadPanel from './components/UploadPanel.jsx'
import ChatWindow from './components/ChatWindow.jsx'

const App = () => {
  return (
    <div  className='relative flex flex-row items-start justify-start gap-3'>
      
     
      <Sidebar />
      <ChatWindow />



    </div>
  )
}

export default App