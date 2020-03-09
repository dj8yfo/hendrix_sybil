import {
    PROTO_AUTH_STARTED,
    PROTO_AUTH_SUCCESS,
    PROTO_AUTH_FAIL,
    PROTO_SELROOM_STARTED,
    PROTO_SELROOM_SUCCESS,
    PROTO_SELROOM_FAIL,
    PROTO_UNKNOWN,
} from '../actions/proto'
import { CONNECT_TO_WS_CLOSED } from '../actions/connectionActions'

const initialState = {
    wsLastMessage: null,
    nym: null,
    pendingMsgToken: '', //false in boolean context
    room: null,
    perPage: null,
    lastMessage: null, //proto - room last msg pointer/counter
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
                room: null,
                perPage: null,
                lastMessage: null,
                wsLastMessage: 'exited lobby',
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
        case PROTO_SELROOM_STARTED:
            return {
                ...state,
                pendingMsgToken: action.payload,
            }
        case PROTO_SELROOM_SUCCESS:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload.token),
                room: action.payload.room,
                perPage: action.payload.perPage,
                lastMessage: action.payload.lastMessage,
            }
        case PROTO_SELROOM_FAIL:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload.token),
            }
        case PROTO_UNKNOWN:
            return {
                ...state,
                wsLastMessage: action.payload,
            }
        default:
            return state
    }
}
