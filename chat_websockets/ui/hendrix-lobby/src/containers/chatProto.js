import React from 'react'
import { connect } from 'react-redux'
//import {} from '../actions/proto'
import './ChatProto.css'

class ChatProto extends React.Component {
    render() {
        const { proto } = this.props
        return (
            <div className="chat-proto">
                <p> authenticated nym: {proto.nym}</p>
                <p> room in: {proto.room} </p>
                <p> msg pending: {proto.pendingMsgToken} </p>
            </div>
        )
    }
}

const mapStateToProps = store => {
    console.log(store)
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
