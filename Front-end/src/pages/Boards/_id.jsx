//Board Details
import Container from '@mui/material/Container'
import AppBar from '~/components/AppBar/AppBar'
import BoardBar from './BoardBar/BoardBar'
import BoardContent from './BoardContent/BoardContent'
import React from 'react'
import axios from "axios"

// Function to fetch board data
const fetchBoardData = async () => {
  try {
    const response = await axios.get(
      "http://127.0.0.1:5000/boards/board-id-01"
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching board data:", error);
    return null;
  }
};
 
function Board() {
  const [boardData, setBoardData] = React.useState(null);

  React.useEffect(() => {
    const loadData = async () => {
      const data = await fetchBoardData();
      setBoardData(data);
    };

    loadData();
  }, []); // Empty dependency array ensures this runs once on component mount

  if (!boardData) {
    return <div>Loading board data...</div>;
  }

  return (
      <Container disableGutters maxWidth={false} sx={{ height: '100vh', backgroundColor: 'primary.main'}}>
        <AppBar />    
        <BoardBar board={boardData} />
        <BoardContent board={boardData} />
      </Container>
  )
}
 
export default Board