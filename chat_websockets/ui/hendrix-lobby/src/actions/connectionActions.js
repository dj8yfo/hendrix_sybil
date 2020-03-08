import { init_authenticate } from './proto.js'
export const CONNECT_TO_WS_REQUEST = 'CONNECT_TO_WS_REQUEST'
export const CONNECT_TO_WS_ESTABLISHED = 'CONNECT_TO_WS_ESTABLISHED'
export const CONNECT_TO_WS_ERRORED = 'CONNECT_TO_WS_ERRORED'
export const CONNECT_TO_WS_CLOSED = 'CONNECT_TO_WS_CLOSED'
export const WS_MESSAGE_RECEIVED = 'WS_MESSAGE_RECEIVED'

//import { v4 as uuidv4 } from 'uuid';

export let conn = null
export function connectToWs() {
    return dispatch => {
        dispatch({
            type: CONNECT_TO_WS_REQUEST,
        })
        conn = new WebSocket(`ws://${window.location.hostname}:8080/ws`)
        conn.onopen = init_authenticate(
            CONNECT_TO_WS_ESTABLISHED,
            dispatch,
            conn
        )
        conn.onerror = function(ev) {
            dispatch({
                type: CONNECT_TO_WS_ERRORED,
                payload: ev,
            })
        }
        conn.onclose = function(ev) {
            dispatch({
                type: CONNECT_TO_WS_CLOSED,
                payload: ev,
            })
        }

        conn.onmessage = function(ev) {
            dispatch({
                type: WS_MESSAGE_RECEIVED,
                payload: ev,
            })
        }
        console.log(conn)
    }
}
