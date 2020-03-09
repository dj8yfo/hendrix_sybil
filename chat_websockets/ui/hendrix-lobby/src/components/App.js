import React from 'react'
import ConnectionStatus from '../containers/connectionStatus.js'
import ChatProto from '../containers/chatProto'
import Messages from '../containers/messages'
import './App.css'

class App extends React.Component {
    render() {
        return (
            <div>
                <header className="App-header">hendrix</header>
                <ConnectionStatus />
                <Messages />
                <ChatProto />
            </div>
        )
    }
}

export default App
