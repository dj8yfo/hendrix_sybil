import React from 'react'
import { connect } from 'react-redux'
import { connectToWs } from '../actions/connectionActions'

class ConnectionStatus extends React.Component {
    render() {
        const { connection, initConnect } = this.props
        return (
            <div className="conn_status">
                <button
                    disabled={connection.connected || connection.connecting}
                    onClick={initConnect}
                >
                    Join lobby
                </button>
                <p> latest message: {connection.message}</p>
                <p>
                    status:{' '}
                    {connection.connected ? 'connected' : 'disconnected'}
                </p>
                {connection.connecting ? <p>Connecting...</p> : null}
                <div>Error: {connection.error}</div>
            </div>
        )
    }
}

const mapStateToProps = store => {
    console.log(store)
    return {
        connection: store.connection,
    }
}

const mapDispatchToProps = dispatch => {
    return {
        initConnect: () => dispatch(connectToWs()),
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ConnectionStatus)
