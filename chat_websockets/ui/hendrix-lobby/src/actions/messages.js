import { v4 as uuidv4 } from 'uuid'
export const PROTO_MSG_RCVD = 'PROTO_MSG_RCVD'
export const PROTO_MSG_CLEAR_NOTIFY = 'PROTO_MSG_CLEAR_NOTIFY'
export const PROTO_MSG_FAIL = 'PROTO_MSG_FAIL'
export const PROTO_HISTORY_GET_STARTED = 'PROTO_HISTORY_GET_STARTED'
export const PROTO_HISTORY_SUCCESS = 'PROTO_HISTORY_SUCCESS'
export const PROTO_HISTORY_FAIL = 'PROTO_HISTORY_FAIL'
export const CHANGED_NEW_MESSAGES_INDICATOR = 'CHANGED_NEW_MESSAGES_INDICATOR'

const flashTimeout = 1000
export function handleRegularMessageRcvd(protoMsg, dispatch) {
    switch (protoMsg.status) {
        case 'success':
            dispatch({
                type: PROTO_MSG_RCVD,
                payload: {
                    content: protoMsg.msg.content,
                    date_created: protoMsg.msg.date_created,
                    from_nym: protoMsg.msg.from_nym,
                    token: protoMsg.msg.token,
                    viewed: false,
                },
            })
            setTimeout(() => {
                dispatch({
                    type: PROTO_MSG_CLEAR_NOTIFY,
                })
            }, flashTimeout)
            break
        case 'error':
            dispatch({
                type: PROTO_MSG_FAIL,
                payload: {
                    token: protoMsg.msg.token,
                },
            })
            break
        default:
            return
    }
}
export function handleHistoryRcvd(protoMsg, dispatch) {
    switch (protoMsg.status) {
        case 'success':
            const msgs = protoMsg.msg.result.map(value => {
                return {
                    content: value.content,
                    date_created: value.date_created,
                    from_nym: value.from_nym,
                    viewed: true,
                }
            })
            dispatch({
                type: PROTO_HISTORY_SUCCESS,
                payload: {
                    token: protoMsg.msg.token,
                    room: protoMsg.msg.room,
                    history: msgs,
                },
            })
            break
        case 'error':
            dispatch({
                type: PROTO_HISTORY_FAIL,
                payload: protoMsg.msg.token,
            })
            break
        default:
            return
    }
}

export const historyRetrieve = (lastMessage, room, connection) => {
    const msgToken = uuidv4()
    let sendmessage = {
        action: 'history_retrieve',
        token: msgToken,
        room: room,
        last_message: lastMessage,
    }
    connection.send(JSON.stringify(sendmessage))
    return {
        type: PROTO_HISTORY_GET_STARTED,
        payload: msgToken,
    }
}

export const indicateNewMessages = messages => {
    return {
        type: CHANGED_NEW_MESSAGES_INDICATOR,
        payload: messages,
    }
}
