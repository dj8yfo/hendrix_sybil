import React from 'react'
import { connect } from 'react-redux'
import { PropTypes } from 'prop-types'
import { MessageEntry } from '../components/MessageEntry'
import { conn } from '../actions/connectionActions'
import { historyRetrieve, indicateNewMessages } from '../actions/messages'
import { compWidth } from '../components/MessageEntry'
import { isMobileLayout, getRandomColor, prevMessages } from '../utils/utils'
import './messages.css'

export let expwidth = compWidth + 200
let imgdim = isMobileLayout ? 500 : 600
class Messages extends React.Component {
    state = {
        lastScrollTop: null,
        maxScroll: null,
        colors: {},
        childrefs: null,
        messages: [],
    }
    constructor(props) {
        super(props)
        this.viewPort = React.createRef()
    }

    historyDisabled(pendingMsgToken, room, lastMessage) {
        return Boolean(pendingMsgToken) || !Boolean(room) || lastMessage < 0
    }

    renderTemplate(messages) {
        this.state.messages = [...this.props.messages.messages] // eslint-disable-line
        this.state.childrefs = [] // eslint-disable-line
        var res = messages.map((value, index) => {
            if (this.state.colors[value.from_nym] === undefined) {
                this.state.colors[value.from_nym] = getRandomColor() // eslint-disable-line
            }
            let newcolor = this.state.colors[value.from_nym]
            let dkey = String(value.date_created) + index
            let result = (
                <MessageEntry
                    key={dkey}
                    value={value}
                    color={newcolor}
                    inputRef={element => {
                        this.state.childrefs.push(element)
                    }}
                />
            )
            return result
        })
        return res
    }
    btnClickHandler = ev => {
        const { lastMessage, room } = this.props.messages
        this.props.historyRetrieve(lastMessage, room)
    }
    checkViewedMessaged(currentScroll) {
        let ifDispatch = false
        let nonEmpty = this.state.childrefs.filter(value => value != null)
        nonEmpty.forEach((value, index) => {
            let bottom = value.offsetHeight + value.offsetTop
            if (currentScroll >= bottom - 5) {
                let prev = this.state.messages[index].viewed
                if (!prev) ifDispatch = true
                this.state.messages[index].viewed = true // eslint-disable-line
            }
        })
        if (ifDispatch) {
            this.props.indicateNewMessages(this.state.messages)
        }
    }
    componentDidUpdate() {
        const st = this.viewPort.current.scrollTop
        const ofhei = this.viewPort.current.offsetHeight

        this.checkViewedMessaged(st + ofhei)
    }

    scrollTopHandler = () => {
        const st = this.viewPort.current.scrollTop
        const ofhei = this.viewPort.current.offsetHeight
        if (this.state.lastScrollTop == null) {
            this.state.lastScrollTop = st <= 0 ? 0 : st // eslint-disable-line
            return
        }
        if (st > this.state.lastScrollTop) {
            this.checkViewedMessaged(st + ofhei)
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

        let colorScroll = notifyFlag ? '#999999' : '#444444'
        let pending = messages.filter(value => value.viewed === false).length
        let hasunviewed = pending > 0
        let arrowshift = (3 * expwidth) / 4
        return (
            <div className="msgs">
                <button
                    key="history-btn-key"
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
                            {this.renderTemplate(messages)}
                        </React.Fragment>
                    )}
                </div>
                {hasunviewed ? (
                    <div
                        className="arrow"
                        style={{
                            left: `${arrowshift}px`,
                            top: '540px',
                        }}
                    >
                        <img
                            alt="scroll-down"
                            width={30}
                            height={30}
                            src="./arrow.png"
                        ></img>
                    </div>
                ) : null}
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
        indicateNewMessages: flag => dispatch(indicateNewMessages(flag)),
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
    historyRetrieve: PropTypes.func.isRequired,
    indicateNewMessages: PropTypes.func.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(Messages)
