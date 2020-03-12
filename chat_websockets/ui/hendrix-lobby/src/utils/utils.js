export function clearToken(state, recvdToken) {
    if (recvdToken === state.pendingMsgToken) {
        return ''
    } else {
        return state.pendingMsgToken
    }
}
