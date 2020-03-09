export const PROTO_MSG_RCVD = 'PROTO_MSG_RCVD'

export function handleRegularMessageRcvd(protoMsg, dispatch) {
    switch (protoMsg.status) {
        case 'success':
            dispatch({
                type: PROTO_MSG_RCVD,
                payload: {
                    content: protoMsg.msg.content,
                    date_created: protoMsg.msg.date_created,
                    from_nym: protoMsg.msg.from_nym,
                    token: protoMsg.msg.token,
                },
            })
            break
        default:
            return
    }
}
