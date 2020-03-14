import React from 'react'
import { connect } from 'react-redux'
import { PropTypes } from 'prop-types'
import { MessageEntry } from '../components/MessageEntry'
import { conn } from '../actions/connectionActions'
import { historyRetrieve } from '../actions/messages'
import { compWidth } from '../components/MessageEntry'
import { isMobileLayout, getRandomColor, prevMessages } from '../utils/utils'
import './messages.css'

export let expwidth = compWidth + 200
let imgdim = isMobileLayout ? 500 : 600
class Messages extends React.Component {
    state = {
        lastScrollTop: null,
        colors: {},
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
            if (this.state.colors[value.from_nym] === undefined) {
                this.state.colors[value.from_nym] = getRandomColor() // eslint-disable-line
            }
            let newcolor = this.state.colors[value.from_nym]
            let dkey = String(value.date_created) + index
            return <MessageEntry key={dkey} value={value} color={newcolor} />
        })
        return res
    }
    btnClickHandler = ev => {
        const { lastMessage, room } = this.props.messages
        this.props.historyRetrieve(lastMessage, room)
    }

    scrollTopHandler = () => {
        const st = this.viewPort.current.scrollTop
        if (this.state.lastScrollTop == null) {
            this.state.lastScrollTop = st <= 0 ? 0 : st // eslint-disable-line
            return
        }
        if (st > this.state.lastScrollTop) {
        } else {
            if (st < 10) {
                const {
                    lastMessage,
                    room,
                    pendingMsgToken,
                } = this.props.messages
                if (!this.historyDisabled(pendingMsgToken, room, lastMessage)) {
                    this.props.historyRetrieve(lastMessage, room)
                }
                if (prevMessages(lastMessage)) {
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
            closedscr,
            notifyFlag,
        } = this.props.messages
        let historyDisabled = this.historyDisabled(
            pendingMsgToken,
            room,
            lastMessage
        )

        console.log(`history disabled: ${historyDisabled}`)
        let colorScroll = notifyFlag ? '#999999' : '#444444'
        return (
            <div className="msgs">
                <div className="centered"></div>

                <div
                    className="viewport"
                    id="containerElement"
                    ref={this.viewPort}
                    onScroll={this.scrollTopHandler}
                    style={{
                        position: 'relative',
                        height: '550px',
                        width: `${expwidth}px`,
                        overflow: 'scroll',
                        overflowX: 'hidden',
                        scrollbarWidth: 'thick',
                        scrollbarColor: `${colorScroll} #000000`,
                        marginBottom: '10px',
                        border: '1px',
                        borderRight: '0px',
                        borderLeft: '0px',
                        borderBottom: '1px',
                        borderStyle: 'solid',
                        borderColor: '#444444',
                        alignItems: 'center',
                    }}
                >
                    {closedscr ? (
                        <div className="centered">
                            <img
                                src="./ecorp.gif"
                                alt="hendrix"
                                width={imgdim}
                                height={imgdim}
                            ></img>
                        </div>
                    ) : (
                        <React.Fragment>
                            <button
                                className="shadowbtn btn"
                                style={{
                                    //width: `${expwidth}px`,
                                    height: '20px',
                                    width: `100%`,
                                }}
                                onClick={this.btnClickHandler}
                                disabled={historyDisabled}
                            >
                                {' '}
                                hist
                            </button>
                            {this.renderTemplate(messages)}
                        </React.Fragment>
                    )}
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
        closed: PropTypes.bool,
        notifyFlag: PropTypes.bool,
    }),
}

export default connect(mapStateToProps, mapDispatchToProps)(Messages)
