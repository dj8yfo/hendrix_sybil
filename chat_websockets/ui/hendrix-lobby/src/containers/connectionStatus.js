import React from 'react'
import { connect } from 'react-redux'
import { PropTypes } from 'prop-types'
import './connectionStatus.css'
import { prevMessages, isMobileLayout } from '../utils/utils'

const alert1 = "You've been resleeved to a stock option: "
const alert2 =
    '\nRegular customers of Hendrix are offered a wide selection of bespoke sleeves.'

class ConnectionStatus extends React.Component {
    computeTooltip() {
        const { proto } = this.props
        return proto.pendingMsgToken || proto.unhandledWsMessage
    }
    render() {
        const { connection, messages, statusLast } = this.props
        let prevMessage = prevMessages(messages.lastMessage)
        let fsize = isMobileLayout() ? '80%' : '100%'
        return (
            <div
                className="stats"
                style={{
                    fontSize: fsize,
                }}
            >
                <p
                    data-tooltip={JSON.stringify(statusLast.info)}
                    data-tooltip-location="right"
                >
                    status:{' '}
                    {connection.authenticating
                        ? 'uploading...'
                        : connection.connected
                        ? 'connected'
                        : connection.connecting
                        ? 'connecting...'
                        : 'disconnected'}
                </p>
                <div>
                    sleeve:{' '}
                    <text
                        data-tooltip={`${alert1}${messages.nym}.\n${alert2}`}
                        data-tooltip-location="right"
                    >
                        {messages.nym}
                    </text>
                </div>
                <p> room: {messages.room}</p>
                <p> prev messages: {prevMessage ? prevMessage : 'None'} </p>

                <div>
                    <div className="block-msg">
                        <text
                            data-tooltip={this.computeTooltip()}
                            data-tooltip-location="right"
                        >
                            σ tip σ
                        </text>
                    </div>
                </div>
            </div>
        )
    }
}

const mapStateToProps = store => {
    return {
        connection: store.connection,
        messages: store.messages,
        proto: store.proto,
        statusLast: store.statusLast,
    }
}

ConnectionStatus.propTypes = {
    connection: PropTypes.shape({
        connected: PropTypes.bool.isRequired,
        connecting: PropTypes.bool.isRequired,
        authenticated: PropTypes.bool.isRequired,
        error: PropTypes.string.isRequired,
    }),
    proto: PropTypes.shape({
        unhandledWsMessage: PropTypes.string,
        pendingMsgToken: PropTypes.string.isRequired,
    }),
}
export default connect(mapStateToProps)(ConnectionStatus)
