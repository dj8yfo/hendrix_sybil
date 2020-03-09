import { v4 as uuidv4 } from 'uuid'
import { handleRegularMessageRcvd } from './messages'
export const PROTO_AUTH_STARTED = 'PROTO_AUTH_STARTED'
export const PROTO_AUTH_SUCCESS = 'PROTO_AUTH_SUCCESS'
export const PROTO_AUTH_FAIL = 'PROTO_AUTH_FAIL'
export const PROTO_SELROOM_STARTED = 'PROTO_SELROOM_STARTED'
export const PROTO_SELROOM_SUCCESS = 'PROTO_SELROOM_SUCCESS'
export const PROTO_SELROOM_FAIL = 'PROTO_SELROOM_FAIL'
export const PROTO_UNKNOWN = 'PROTO_UNKNOWN'

const defaultRoom = 'Lobby'

export function initAuthenticate(connection) {
    return dispatch => {
        const msgToken = uuidv4()
        const authmessage = {
            action: 'authenticate',
            token: msgToken,
        }
        window.prompt('Please, enter the desired sleeve model:', 'Khumalo ...')
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

export function message_received(dispatch, connection) {
    return ev => {
        let protoMsg
        try {
            protoMsg = JSON.parse(ev.data)
        } catch (err) {
            console.log(`${err} - json.parse?`)
            dispatch({
                type: PROTO_UNKNOWN,
                payload: ev.data,
            })
            return
        }
        switch (protoMsg.msg.action) {
            case 'authenticate':
                console.log('authenticate msg received')
                handleAuthenticate(protoMsg, dispatch, connection)
                break
            case 'select_room':
                console.log('select_room msg received')
                handleSelectRoom(protoMsg, dispatch)
                break
            case 'send_message':
                handleRegularMessageRcvd(protoMsg, dispatch)
                break
            default:
                dispatch({
                    type: PROTO_UNKNOWN,
                    payload: ev.data,
                })
        }
    }
}
const alert1 = "You've been resleeved to a stock option:"
const alert2 =
    '\nRegular customers of Hendrix are offered a wide selection of bespoke sleeves.'
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
            alert(`${alert1} ${protoMsg.msg.from_nym}. ${alert2}`)
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
