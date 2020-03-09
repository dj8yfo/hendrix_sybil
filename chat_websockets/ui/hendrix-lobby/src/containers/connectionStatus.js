import React from 'react'
import { connect } from 'react-redux'
import {
    connectToWs,
    connectionClose,
    conn,
} from '../actions/connectionActions'
import { initAuthenticate } from '../actions/proto'
import './connectionStatus.css'

class ConnectionStatus extends React.Component {
    render() {
        console.log('<ConnectionStatus/ >')
        const { connection, initConnect, initAuthenticate } = this.props
        return (
            <div>
                <div className="centered">
                    <button
                        className="btn"
                        disabled={connection.connected || connection.connecting}
                        onClick={initConnect}
                    >
                        enter lobby
                    </button>
                </div>
                <div className="centered">
                    <button
                        className="btn"
                        disabled={
                            connection.authenticated ||
                            !connection.connected ||
                            connection.connecting
                        }
                        onClick={initAuthenticate}
                    >
                        choose a sleeve
                    </button>
                </div>
                <div className="centered">
                    <button
                        className="btn"
                        disabled={
                            !(connection.connected || connection.connecting)
                        }
                        onClick={connectionClose}
                    >
                        leave hendrix
                    </button>
                </div>
                <div>
                    <p>
                        status:{' '}
                        {connection.connected ? 'connected' : 'disconnected'}
                    </p>
                    {connection.connecting ? <p>Connecting...</p> : null}
                    <div>Error: {connection.error}</div>
                </div>
            </div>
        )
    }
}

const mapStateToProps = store => {
    return {
        connection: store.connection,
    }
}

const mapDispatchToProps = dispatch => {
    return {
        initConnect: () => dispatch(connectToWs()),
        initAuthenticate: () => dispatch(initAuthenticate(conn)),
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ConnectionStatus)
