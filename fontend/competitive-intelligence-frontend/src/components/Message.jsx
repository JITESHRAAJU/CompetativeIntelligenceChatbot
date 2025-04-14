import React from 'react';

function Message({ message }) {
  const { type, content } = message;
  
  return (
    <div className={`message ${type}`}>
      <div className="message-avatar">
        {type === 'user' ? (
          <div className="avatar user">👤</div>
        ) : type === 'assistant' ? (
          <div className="avatar assistant">🤖</div>
        ) : (
          <div className="avatar system">ℹ️</div>
        )}
      </div>
      <div className="message-content">
        {content.split('\n').map((line, i) => (
          <React.Fragment key={i}>
            {line}
            {i < content.split('\n').length - 1 && <br />}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export default Message;