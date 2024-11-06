import Board from '~/pages/Boards/_id'
import { GlobalStateProvider } from '~/utils/NewCardId'

function App() {
  return (
    <GlobalStateProvider>
      <Board />
    </GlobalStateProvider>
  )
}

export default App
