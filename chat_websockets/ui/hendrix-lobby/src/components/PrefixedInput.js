import React from 'react'
import './PrefixedInput.css'

export const PrefixedInput = () => {
    return (
        <div>
            <input className="prefixed-input" type="text" />
            <span className="inside-prefixed-input">$</span>
        </div>
    )
}
