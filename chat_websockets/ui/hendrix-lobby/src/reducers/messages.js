import { PROTO_SELROOM_SUCCESS } from '../actions/proto'
import { PROTO_MSG_RCVD } from '../actions/messages'
import { CONNECT_TO_WS_CLOSED } from '../actions/connectionActions'

const initialState = {
    messages: [],
    lastMessage: null, //proto - room last msg pointer/counter
}

export function messagesReducer(state = initialState, action) {
    switch (action.type) {
        case CONNECT_TO_WS_CLOSED:
            return {
                ...state,
                messages: [],
            }
        case PROTO_SELROOM_SUCCESS:
            return {
                ...state,
                messages: [],
                lastMessage: action.payload.lastMessage,
            }
        case PROTO_MSG_RCVD:
            return {
                ...state,
                messages: [...state.messages, action.payload],
            }
        default:
            return state
    }
}
