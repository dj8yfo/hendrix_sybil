import React from 'react'
import { connect } from 'react-redux'
import { PropTypes } from 'prop-types'
import { MessageEntry } from '../components/MessageEntry'
import { conn } from '../actions/connectionActions'
import { historyRetrieve } from '../actions/messages'
import './messages.css'

const alert1 = "You've been resleeved to a stock option: "
const alert2 =
    '\nRegular customers of Hendrix are offered a wide selection of bespoke sleeves.'

class Messages extends React.Component {
    state = {
        lastScrollTop: null,
    }
    constructor(props) {
        super(props)
        this.viewPort = React.createRef()
    }

    historyDisabled(pendingMsgToken, room, lastMessage) {
        return Boolean(pendingMsgToken) || !Boolean(room) || lastMessage < 0
    }
    renderTemplate(messages) {
        var res = messages.map((value, index) => {
            let dkey = String(value.date_created) + index
            return <MessageEntry key={dkey} value={value} />
        })
        return res
    }
    btnClickHandler = ev => {
        const { lastMessage, room } = this.props.messages
        this.props.historyRetrieve(lastMessage, room)
    }

    prevMessages(lastMessage) {
        if (lastMessage == null) {
            return 0
        }
        let prevMessage = lastMessage > -1 ? lastMessage + 1 : null
        return prevMessage > 0 ? prevMessage : 0
    }
    scrollTopHandler = () => {
        const st = this.viewPort.current.scrollTop
        if (this.state.lastScrollTop == null) {
            this.state.lastScrollTop = st <= 0 ? 0 : st // eslint-disable-line
            return
        }
        if (st > this.state.lastScrollTop) {
        } else {
            if (st < 50) {
                const {
                    lastMessage,
                    room,
                    pendingMsgToken,
                } = this.props.messages
                if (!this.historyDisabled(pendingMsgToken, room, lastMessage)) {
                    this.props.historyRetrieve(lastMessage, room)
                }
                if (this.prevMessages(lastMessage)) {
                    this.viewPort.current.scrollTop = this.state.lastScrollTop
                    return
                }
            }
        }
        this.state.lastScrollTop = st <= 0 ? 0 : st // eslint-disable-line
    }
    render() {
        console.log('<Messages/ >')
        const {
            messages,
            pendingMsgToken,
            room,
            lastMessage,
            nym,
        } = this.props.messages
        let historyDisabled = this.historyDisabled(
            pendingMsgToken,
            room,
            lastMessage
        )

        let prevMessage = this.prevMessages(lastMessage)
        console.log(`history disabled: ${historyDisabled}`)
        return (
            <div className="msgs">
                <p> Messages </p>
                <div>
                    your sleeve:{'  '}
                    <div className="tooltip">
                        {nym}
                        <div className="tooltiptext">
                            <p>{`${alert1}${nym}.`}</p>
                            <p>{`${alert2}`}</p>
                        </div>
                    </div>
                </div>
                <p> room: {room}</p>
                {prevMessage ? <p> prev messages: {prevMessage} </p> : null}
                <button
                    className="btn"
                    onClick={this.btnClickHandler}
                    disabled={historyDisabled}
                >
                    {' '}
                    hist
                </button>

                <div
                    className="viewport"
                    id="containerElement"
                    ref={this.viewPort}
                    onScroll={this.scrollTopHandler}
                    style={{
                        position: 'relative',
                        height: '600px',
                        width: '600px',
                        overflow: 'scroll',
                        overflowX: 'hidden',
                        scrollbarWidth: 'thin',
                        scrollbarColor: '#444444 #000000',
                        marginBottom: '30px',
                        border: '1px',
                        borderRight: '0px',
                        borderLeft: '0px',
                        borderBottom: '1px',
                        borderStyle: 'solid',
                        borderColor: '#444444',
                    }}
                >
                    {this.renderTemplate(messages)}
                </div>
            </div>
        )
    }
}

const mapStateToProps = store => {
    return {
        messages: store.messages,
    }
}

const mapDispatchToProps = dispatch => {
    return {
        historyRetrieve: (lastMessage, room) =>
            dispatch(historyRetrieve(lastMessage, room, conn)),
    }
}

Messages.propTypes = {
    messages: PropTypes.shape({
        messages: PropTypes.array.isRequired,
        nym: PropTypes.string,
        lastMessage: PropTypes.number,
        room: PropTypes.string,
        perPage: PropTypes.number,
        pendingMsgToken: PropTypes.string.isRequired,
    }),
}

export default connect(mapStateToProps, mapDispatchToProps)(Messages)
