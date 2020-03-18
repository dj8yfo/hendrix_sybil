import { message_received } from './proto.js'
export const CONNECT_TO_WS_REQUEST = 'CONNECT_TO_WS_REQUEST'
export const CONNECT_TO_WS_ESTABLISHED = 'CONNECT_TO_WS_ESTABLISHED'
export const CONNECT_TO_WS_ERRORED = 'CONNECT_TO_WS_ERRORED'
export const CONNECT_TO_WS_CLOSED = 'CONNECT_TO_WS_CLOSED'

export let conn = null
export function connectToWs() {
    return dispatch => {
        dispatch({
            type: CONNECT_TO_WS_REQUEST,
        })
        conn = new WebSocket(`ws://${window.location.host}/ws`)
        //conn = new WebSocket(`wss://${window.location.hostname}:443/ws`)
        conn.onopen = function(ev) {
            dispatch({
                type: CONNECT_TO_WS_ESTABLISHED,
                payload: ev,
            })
        }

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

        conn.onmessage = message_received(dispatch, conn)
    }
}

export function connectionClose() {
    conn.close()
}
