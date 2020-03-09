import React from 'react'
import { connect } from 'react-redux'
//import {} from '../actions/proto'
import { PrefixedInput } from '../components/PrefixedInput'
import './ChatProto.css'

class ChatProto extends React.Component {
    render() {
        console.log('<ChatProto/ >')
        const { proto } = this.props
        return (
            <div className="chat-proto">
                <p> latest message: {proto.wsLastMessage}</p>
                <p> authenticated nym: {proto.nym}</p>
                <p> room in: {proto.room} </p>
                <p> msg pending: {proto.pendingMsgToken} </p>
                <p> per page paging: {proto.perPage} </p>
                <p>
                    {' '}
                    last message counter of {proto.room}: {proto.lastMessage}{' '}
                </p>
                <PrefixedInput />
            </div>
        )
    }
}

const mapStateToProps = store => {
    return {
        proto: store.proto,
    }
}

//const mapDispatchToProps = dispatch => {
//    return {
//        initConnect: () => dispatch(connectToWs()),
//    }
//}

export default connect(mapStateToProps)(ChatProto)
