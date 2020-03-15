import React from 'react'
import { PropTypes } from 'prop-types'
import { connect } from 'react-redux'
//import {} from '../actions/proto'
import { PrefixedInput } from '../components/PrefixedInput'
import { conn } from '../actions/connectionActions'
import { sendMessage, sendQueryMenu, initSelectroom } from '../actions/proto'
import './ChatProto.css'

class ChatProto extends React.Component {
    render() {
        const { proto, sendMessage, sendQueryMenu, initSelectroom } = this.props
        let sendDisabled =
            Boolean(proto.pendingMsgToken) || !Boolean(proto.room)
        let menu = proto.room === 'Lobby' ? sendQueryMenu : () => {}
        return (
            <div className="chat-proto">
                <PrefixedInput
                    sender={sendMessage}
                    query={menu}
                    changeRoom={initSelectroom}
                    disabled={sendDisabled}
                />
            </div>
        )
    }
}

const mapStateToProps = store => {
    return {
        proto: store.proto,
    }
}

const mapDispatchToProps = dispatch => {
    return {
        sendMessage: message => dispatch(sendMessage(message, conn)),
        sendQueryMenu: () => dispatch(sendQueryMenu(conn)),
        initSelectroom: destinationRoom =>
            dispatch(initSelectroom(conn, destinationRoom)),
    }
}

ChatProto.propTypes = {
    proto: PropTypes.shape({
        unhandledWsMessage: PropTypes.string,
        nym: PropTypes.string,
        pendingMsgToken: PropTypes.string.isRequired,
        room: PropTypes.string,
        perPage: PropTypes.number,
        lastMessage: PropTypes.number,
    }),
    sendMessage: PropTypes.func.isRequired,
    sendQueryMenu: PropTypes.func.isRequired,
    initSelectroom: PropTypes.func.isRequired,
}
export default connect(mapStateToProps, mapDispatchToProps)(ChatProto)
