import { v4 as uuidv4 } from 'uuid'
export const PROTO_AUTH_STARTED = 'PROTO_AUTH_STARTED'
export const PROTO_AUTH_SUCCESS = 'PROTO_AUTH_SUCCESS'
export const PROTO_AUTH_FAIL = 'PROTO_AUTH_FAIL'

export function initAuthenticate(connection) {
    return dispatch => {
        const msgToken = uuidv4()
        const authmessage = {
            action: 'authenticate',
            token: msgToken,
        }
        window.prompt('Please choose a sleeve:', '')
        dispatch({
            type: PROTO_AUTH_STARTED,
            payload: msgToken,
        })
        connection.send(JSON.stringify(authmessage))
    }
}

export function message_received(type, dispatch, connection) {
    return ev => {
        dispatch({
            type: type,
            payload: ev,
        })

        let protoMsg = JSON.parse(ev.data)
        switch (protoMsg.msg.action) {
            case 'authenticate':
                console.log('authenticate msg received')
                handle_authenticate(protoMsg, dispatch, connection)
                break
            default:
                console.log('unknown action message received')
        }
    }
}
const alert1 = 'You have been granted a stock sleeve:'
const alert2 =
    '\nRegular customers of Hendrix are offered a wide selection of bespoke sleeves.'
function handle_authenticate(protoMsg, dispatch, connection) {
    switch (protoMsg.status) {
        case 'success':
            alert(`${alert1} ${protoMsg.msg.from_nym}. ${alert2}`)
            dispatch({
                type: PROTO_AUTH_SUCCESS,
                payload: {
                    token: protoMsg.msg.token,
                    nym: protoMsg.msg.from_nym,
                },
            })
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
