import {
    PROTO_AUTH_STARTED,
    PROTO_AUTH_SUCCESS,
    PROTO_AUTH_FAIL,
    PROTO_SELROOM_STARTED,
    PROTO_SELROOM_SUCCESS,
    PROTO_SELROOM_FAIL,
    PROTO_UNKNOWN,
    PROTO_SEND_MSG,
} from '../actions/proto'
import {
    PROTO_MSG_RCVD,
    PROTO_MSG_FAIL,
    PROTO_HISTORY_GET_STARTED,
    PROTO_HISTORY_FAIL,
    PROTO_HISTORY_SUCCESS,
} from '../actions/messages'
import {
    CONNECT_TO_WS_CLOSED,
    CONNECT_TO_WS_ESTABLISHED,
} from '../actions/connectionActions'
import { clearToken } from '../utils/utils'

const initialState = {
    unhandledWsMessage: null,
    nym: null,
    pendingMsgToken: '', //false in boolean context
    room: null,
    perPage: null,
    lastMessage: null, //proto - room last msg pointer/counter
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
                unhandledWsMessage: 'left Hendrix',
            }
        case CONNECT_TO_WS_ESTABLISHED:
            return {
                ...state,
                unhandledWsMessage: 'shall set foot on Hendrix threshold',
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
                unhandledWsMessage: 'consciousness uploaded',
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
        case PROTO_SEND_MSG:
            return {
                ...state,
                pendingMsgToken: action.payload,
            }
        case PROTO_MSG_RCVD:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload.token),
            }
        case PROTO_MSG_FAIL:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload.token),
            }
        case PROTO_HISTORY_GET_STARTED:
            return {
                ...state,
                pendingMsgToken: action.payload,
            }
        case PROTO_HISTORY_FAIL:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload),
            }
        case PROTO_HISTORY_SUCCESS:
            return {
                ...state,
                pendingMsgToken: clearToken(state, action.payload.token),
            }
        case PROTO_UNKNOWN:
            return {
                ...state,
                unhandledWsMessage: action.payload,
            }
        default:
            return state
    }
}
