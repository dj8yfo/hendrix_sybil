import { v4 as uuidv4 } from 'uuid'
import { handleRegularMessageRcvd, handleHistoryRcvd } from './messages'
export const PROTO_AUTH_STARTED = 'PROTO_AUTH_STARTED'
export const PROTO_AUTH_SUCCESS = 'PROTO_AUTH_SUCCESS'
export const PROTO_AUTH_FAIL = 'PROTO_AUTH_FAIL'
export const PROTO_SELROOM_STARTED = 'PROTO_SELROOM_STARTED'
export const PROTO_SELROOM_SUCCESS = 'PROTO_SELROOM_SUCCESS'
export const PROTO_SELROOM_FAIL = 'PROTO_SELROOM_FAIL'
export const PROTO_SEND_MSG = 'PROTO_SEND_MSG'
export const PROTO_UNKNOWN = 'PROTO_UNKNOWN'
export const PROTO_GENERIC = 'PROTO_GENERIC'
export const PROTO_STUB_ACTION = 'PROTO_STUB_ACTION'

const defaultRoom = 'Lobby'

export function initAuthenticate(connection) {
    return dispatch => {
        const msgToken = uuidv4()
        const authmessage = {
            action: 'authenticate',
            token: msgToken,
        }
        dispatch({
            type: PROTO_AUTH_STARTED,
            payload: msgToken,
        })
        connection.send(JSON.stringify(authmessage))
    }
}
export function initSelectroom(connection, dstRoom) {
    return dispatch => {
        const msgToken = uuidv4()
        const selectRoomMessage = {
            action: 'select_room',
            destination_room: dstRoom,
            token: msgToken,
        }
        dispatch({
            type: PROTO_SELROOM_STARTED,
            payload: msgToken,
        })
        connection.send(JSON.stringify(selectRoomMessage))
    }
}

export const sendMessage = (message, connection) => {
    const msgToken = uuidv4()
    let sendmessage = {
        action: 'send_message',
        token: msgToken,
        content: message,
    }
    connection.send(JSON.stringify(sendmessage))
    return {
        type: PROTO_SEND_MSG,
        payload: msgToken,
    }
}

export const sendQueryMenu = connection => {
    const msgToken = uuidv4()
    let sendmessage = {
        action: 'query',
        token: msgToken,
        query_name: '/menu',
        parameters: {},
    }
    connection.send(JSON.stringify(sendmessage))
    return {
        type: PROTO_SEND_MSG,
        payload: msgToken,
    }
}

export function message_received(dispatch, connection) {
    return ev => {
        let protoMsg
        try {
            protoMsg = JSON.parse(ev.data)
        } catch (err) {
            dispatch({
                type: PROTO_UNKNOWN,
                payload: ev.data,
            })
            return
        }
        dispatch({
            type: PROTO_GENERIC,
            payload: protoMsg,
        })
        switch (protoMsg.msg.action) {
            case 'authenticate':
                handleAuthenticate(protoMsg, dispatch, connection)
                break
            case 'select_room':
                handleSelectRoom(protoMsg, dispatch)
                break
            case 'send_message':
                handleRegularMessageRcvd(protoMsg, dispatch)
                break
            case 'history_retrieve':
                handleHistoryRcvd(protoMsg, dispatch)
                break
            default:
                dispatch({
                    type: PROTO_UNKNOWN,
                    payload: ev.data,
                })
        }
    }
}
function handleAuthenticate(protoMsg, dispatch, connection) {
    switch (protoMsg.status) {
        case 'success':
            dispatch({
                type: PROTO_AUTH_SUCCESS,
                payload: {
                    token: protoMsg.msg.token,
                    nym: protoMsg.msg.from_nym,
                },
            })
            initSelectroom(connection, defaultRoom)(dispatch)
            break
        case 'error':
            dispatch({
                type: PROTO_AUTH_FAIL,
                payload: {
                    token: protoMsg.msg.token,
                },
            })
            break
        default:
            return
    }
}

function handleSelectRoom(protoMsg, dispatch) {
    switch (protoMsg.status) {
        case 'success':
            dispatch({
                type: PROTO_SELROOM_SUCCESS,
                payload: {
                    token: protoMsg.msg.token,
                    room: protoMsg.msg.room,
                    perPage: protoMsg.msg.page,
                    lastMessage: protoMsg.msg.last_message,
                },
            })
            break
        case 'error':
            dispatch({
                type: PROTO_SELROOM_FAIL,
                payload: {
                    token: protoMsg.msg.token,
                },
            })
            break
        default:
            return
    }
}
