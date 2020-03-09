import {
    PROTO_AUTH_STARTED,
    PROTO_AUTH_SUCCESS,
    PROTO_AUTH_FAIL,
} from '../actions/proto'
import { CONNECT_TO_WS_CLOSED } from '../actions/connectionActions'

const initialState = {
    nym: null,
    pendingMsgToken: '', //false in boolean context
    room: null,
}

function clearToken(state, recvdToken) {
    if (recvdToken === state.pendingMsgToken) {
        return ''
    } else {
        return state.pendingMsgToken
    }
}

export function protoReducer(state = initialState, action) {
    switch (action.type) {
        case CONNECT_TO_WS_CLOSED:
            return {
                ...state,
                pendingMsgToken: '',
                nym: null,
            }
        case PROTO_AUTH_STARTED:
            return {
                ...state,
                pendingMsgToken: action.payload,
            }
        case PROTO_AUTH_SUCCESS:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload.token),
                nym: action.payload.nym,
            }
        case PROTO_AUTH_FAIL:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload.token),
            }
        default:
            return state
    }
}
