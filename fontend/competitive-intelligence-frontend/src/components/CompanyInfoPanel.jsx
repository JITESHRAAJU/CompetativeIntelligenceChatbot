import React, { useState } from 'react';

function CompanyInfoPanel({ industry, competitors, updateIndustry, updateCompetitors }) {
  const [tempIndustry, setTempIndustry] = useState(industry);
  const [tempCompetitor, setTempCompetitor] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const handleIndustryUpdate = () => {
    updateIndustry(tempIndustry);
    setIsEditing(false);
  };

  const addCompetitor = () => {
    if (tempCompetitor.trim() && !competitors.includes(tempCompetitor.trim())) {
      updateCompetitors([...competitors, tempCompetitor.trim()]);
      setTempCompetitor('');
    }
  };

  const removeCompetitor = (competitor) => {
    updateCompetitors(competitors.filter(comp => comp !== competitor));
  };

  return (
    <div className="company-info-panel">
      <h2>Company Information</h2>
      
      <div className="info-section">
        <h3>Industry</h3>
        {!isEditing ? (
          <div className="info-display">
            <p>{industry || 'Not specified'}</p>
            <button className="edit-button" onClick={() => setIsEditing(true)}>
              Edit
            </button>
          </div>
        ) : (
          <div className="edit-form">
            <input
              type="text"
              value={tempIndustry}
              onChange={(e) => setTempIndustry(e.target.value)}
              placeholder="e.g., Technology, Healthcare"
            />
            <button onClick={handleIndustryUpdate}>Save</button>
          </div>
        )}
      </div>
      
      <div className="info-section">
        <h3>Competitors</h3>
        <div className="competitors-list">
          {competitors.length > 0 ? (
            competitors.map((comp, index) => (
              <div key={index} className="competitor-tag">
                <span>{comp}</span>
                <button onClick={() => removeCompetitor(comp)}>×</button>
              </div>
            ))
          ) : (
            <p className="no-items">No competitors added</p>
          )}
        </div>
        <div className="add-competitor">
          <input
            type="text"
            value={tempCompetitor}
            onChange={(e) => setTempCompetitor(e.target.value)}
            placeholder="Add a competitor"
          />
          <button onClick={addCompetitor}>Add</button>
        </div>
      </div>
    </div>
  );
}

export default CompanyInfoPanel;