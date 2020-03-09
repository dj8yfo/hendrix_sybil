import {
    CONNECT_TO_WS_REQUEST,
    CONNECT_TO_WS_ESTABLISHED,
    CONNECT_TO_WS_ERRORED,
    CONNECT_TO_WS_CLOSED,
} from '../actions/connectionActions.js'
import { PROTO_AUTH_SUCCESS } from '../actions/proto'
const initialState = {
    connected: false,
    connecting: false,
    authenticated: false,
    error: '',
}

export function connectionReducer(state = initialState, action) {
    switch (action.type) {
        case CONNECT_TO_WS_REQUEST:
            return {
                ...state,
                connecting: true,
            }
        case CONNECT_TO_WS_ERRORED:
            return {
                ...state,
                connecting: false,
                error: action.payload.type,
            }
        case CONNECT_TO_WS_ESTABLISHED:
            return {
                ...state,
                connecting: false,
                connected: true,
            }
        case CONNECT_TO_WS_CLOSED:
            return {
                ...state,
                connecting: false,
                connected: false,
                authenticated: false,
            }
        case PROTO_AUTH_SUCCESS:
            return {
                ...state,
                authenticated: true,
            }
        default:
            return state
    }
}
