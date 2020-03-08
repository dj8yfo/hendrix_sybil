import {
    CONNECT_TO_WS_REQUEST,
    CONNECT_TO_WS_ESTABLISHED,
    CONNECT_TO_WS_ERRORED,
    CONNECT_TO_WS_CLOSED,
    WS_MESSAGE_RECEIVED,
} from '../actions/connectionActions.js'
const initialState = {
    message: 'not initialized',
    connected: false,
    connecting: false,
    error: '',
}

export function connectionReducer(state = initialState, action) {
    switch (action.type) {
        case CONNECT_TO_WS_REQUEST:
            return {
                ...state,
                connecting: true,
                message: 'connecting...',
            }
        case CONNECT_TO_WS_ERRORED:
            console.log(action.payload)
            return {
                ...state,
                connecting: false,
                message: '',
                error: action.payload.type,
            }
        case CONNECT_TO_WS_ESTABLISHED:
            console.log(action.payload)
            return {
                ...state,
                connecting: false,
                connected: true,
                message: 'inside of a room lobby',
            }
        case CONNECT_TO_WS_CLOSED:
            console.log(action.payload)
            return {
                ...state,
                connecting: false,
                connected: false,
                message: 'exited lobby',
            }
        case WS_MESSAGE_RECEIVED:
            console.log(JSON.parse(action.payload.data))
            return {
                ...state,
                message: action.payload.data,
            }
        default:
            return state
    }
}
