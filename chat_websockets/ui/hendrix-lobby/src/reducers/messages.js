import { PROTO_SELROOM_SUCCESS, PROTO_AUTH_SUCCESS } from '../actions/proto'
import {
    PROTO_MSG_RCVD,
    PROTO_HISTORY_GET_STARTED,
    PROTO_HISTORY_FAIL,
    PROTO_HISTORY_SUCCESS,
} from '../actions/messages'
import { CONNECT_TO_WS_CLOSED } from '../actions/connectionActions'
import { clearToken } from '../utils/utils'

const initialState = {
    messages: [],
    nym: null,
    lastMessage: null, //proto - room last msg pointer/counter
    room: null,
    perPage: null,
    pendingMsgToken: '',
}

export function messagesReducer(state = initialState, action) {
    switch (action.type) {
        case CONNECT_TO_WS_CLOSED:
            return {
                ...state,
                messages: [],
                pendingMsgToken: '',
                lastMessage: null,
                room: null,
                perPage: null,
                nym: null,
            }
        case PROTO_AUTH_SUCCESS:
            return {
                ...state,
                nym: action.payload.nym,
            }
        case PROTO_SELROOM_SUCCESS:
            return {
                ...state,
                messages: [],
                lastMessage: action.payload.lastMessage,
                room: action.payload.room,
                perPage: action.payload.perPage,
            }
        case PROTO_MSG_RCVD:
            return {
                ...state,
                messages: [...state.messages, action.payload],
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
            if (state.room === action.payload.room) {
                return {
                    ...state,
                    lastMessage: state.lastMessage - state.perPage,
                    messages: [...action.payload.history, ...state.messages],
                    pendingMsgToken: clearToken(state, action.payload.token),
                }
            } else {
                return {
                    ...state,
                    pendingMsgToken: clearToken(state, action.payload.token),
                }
            }
        default:
            return state
    }
}
