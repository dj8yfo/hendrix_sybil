import React from 'react'
import { connect } from 'react-redux'
import { PropTypes } from 'prop-types'
import {
    connectToWs,
    connectionClose,
    conn,
} from '../actions/connectionActions'
import { initAuthenticate } from '../actions/proto'
import './connectionButtons.css'

class ConnectionButtons extends React.Component {
    render() {
        const { connection, initConnect, initAuthenticate } = this.props
        return (
            <div
                className="cell"
                style={{
                    paddingRight: '20px',
                }}
            >
                <button
                    className="darkbtn btn"
                    disabled={connection.connected || connection.connecting}
                    onClick={initConnect}
                >
                    enter lobby
                </button>
                <button
                    className="darkbtn btn"
                    disabled={
                        connection.authenticated ||
                        !connection.connected ||
                        connection.connecting
                    }
                    onClick={initAuthenticate}
                >
                    upload consciousness
                </button>
                <button
                    className="darkbtn btn"
                    disabled={!(connection.connected || connection.connecting)}
                    onClick={connectionClose}
                >
                    leave hendrix
                </button>
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

ConnectionButtons.propTypes = {
    connection: PropTypes.shape({
        connected: PropTypes.bool.isRequired,
        connecting: PropTypes.bool.isRequired,
        authenticated: PropTypes.bool.isRequired,
        error: PropTypes.string.isRequired,
    }),
    initConnect: PropTypes.func.isRequired,
    initAuthenticate: PropTypes.func.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(ConnectionButtons)
