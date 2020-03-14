import React from 'react'
import ConnectionStatus from '../containers/connectionStatus.js'
import ChatProto from '../containers/chatProto'
import Messages, { expwidth } from '../containers/messages'
import ConnectionButtons from '../containers/connectionButtons'
import './App.css'
import { isMobileLayout } from '../utils/utils'

class App extends React.Component {
    render() {
        return (
            <div className={isMobileLayout() ? 'not-centered' : 'centered'}>
                <div>
                    <div
                        className="table"
                        style={{
                            width: expwidth,
                        }}
                    >
                        <div className="group-header greyish">
                            <div className="cell stats">
                                <ConnectionStatus />
                            </div>
                            <div className="cell">
                                <div className="App-header">hendrix</div>
                            </div>
                            <ConnectionButtons />
                        </div>
                    </div>
                    <Messages />
                    <ChatProto />
                </div>
            </div>
        )
    }
}

export default App
