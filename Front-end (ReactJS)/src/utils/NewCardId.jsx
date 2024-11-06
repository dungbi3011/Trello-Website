import React from 'react';

const CardIdContext = React.createContext();

const GlobalStateProvider = ({ children }) => {
  const [newCardId, setNewCardId] = React.useState(14); // Initial card ID

  const incrementCardId = () => {
    setNewCardId(newCardId + 1);
  };

  return (
    <CardIdContext.Provider value={{ newCardId, incrementCardId }}>
      {children}
    </CardIdContext.Provider>
  );
};

export { CardIdContext, GlobalStateProvider };