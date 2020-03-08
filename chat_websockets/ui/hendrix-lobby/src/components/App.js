import React from 'react'
import ConnectionStatus from '../containers/connectionStatus.js'
import './App.css'

class App extends React.Component {
    render() {
        return (
            <div>
                <header className="App-header">App header beautiful</header>
                <ConnectionStatus />
            </div>
        )
    }
}

export default App
