import React from "react"
import { mockData } from "~/apis/mock-data"
import Box from "@mui/material/Box"
import Column from "./Column/Column"
import Button from "@mui/material/Button"
import NoteAddIcon from "@mui/icons-material/NoteAdd"
import TextField from "@mui/material/TextField"
import CloseIcon from "@mui/icons-material/Close"
import {
  SortableContext,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable"

function ListColumns({ columns, setOrderedColumns }) {
  const [openNewColumnForm, setOpenNewColumnForm] = React.useState(false)
  const toggleOpenNewColumnForm = () =>
    setOpenNewColumnForm(!openNewColumnForm)

  const [newColumnTitle, setNewColumnTitle] = React.useState("")
  const [newColumnId, setNewColumnId] = React.useState(5)
  const addNewColumn = () => {
    if (!newColumnTitle) {
      alert("Column title can not be empty!")
      return
    }
    const newColumn = {
      _id: `column-id-0${newColumnId}`,
      boardId: "board-id-01",
      title: newColumnTitle,
      cardOrderIds: [`column-id-0${newColumnId}-placeholder-card`],
      cards: [
        { 
          _id: `column-id-0${newColumnId}-placeholder-card`, 
          boardId: 'board-id-01', 
          columnId: `column-id-0${newColumnId}`,
          FE_PlaceholderCard: true
        },
      ],
    }
    // mockData.board.columnOrderIds.add(newColumn._id)
    setOrderedColumns([...columns, newColumn])
    toggleOpenNewColumnForm()
    setNewColumnId(newColumnId + 1)
  }

  return (
    <SortableContext
      items={columns?.map((c) => c._id)}
      strategy={horizontalListSortingStrategy}
    >
      <Box
        sx={{
          bgcolor: "inherit",
          width: "100%",
          height: "100%",
          display: "flex",
          overflowX: "auto",
          overflowY: "hidden",
          "&::-webkit-scrollbar-track": { m: 2 },
        }}
      >
        {columns?.map((column) => (
          <Column key={column._id} column={column} setOrderedColumns={setOrderedColumns} />
        ))}
        {/* Box Add new column CTA */}
        {!openNewColumnForm ? (
          <Box
            onClick={toggleOpenNewColumnForm}
            sx={{
              minWidth: "250px",
              maxWidth: "250px",
              mx: 2,
              borderRadius: "6px",
              height: "fit-content",
              bgcolor: "#ffffff3d",
            }}
          >
            <Button
              startIcon={<NoteAddIcon />}
              sx={{
                color: "white",
                width: "100%",
                justifyContent: "flex-start",
                pl: 2.5,
                py: 1,
              }}
            >
              Add another list
            </Button>
          </Box>
        ) : (
          <Box
            sx={{
              minWidth: "250px",
              maxWidth: "250px",
              mx: 2,
              p: 1,
              borderRadius: "6px",
              height: "fit-content",
              bgcolor: "#ffffff3d",
              display: "flex",
              flexDirection: "column",
              gap: 1,
            }}
          >
            <TextField
              label="Enter column title"
              type="text"
              size="small"
              variant="outlined"
              autoFocus
              value={newColumnTitle}
              onChange={(e) => setNewColumnTitle(e.target.value)}
              sx={{
                "& label": { color: "white " },
                "& input": { color: "white " },
                "& label.Mui-focused": { color: "white " },
                "& .MuiOutlinedInput-root": {
                  "& fieldset": { borderColor: "white" },
                  "&:hover fieldset": { borderColor: "white" },
                  "&.Mui-focused fieldset": { borderColor: "white" },
                },
              }}
            />
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Button
                onClick={addNewColumn}
                variant="contained"
                color="success"
                size="small"
                sx={{
                  boxShadow: "none",
                  border: "0.5px solid",
                  borderColor: (theme) => theme.palette.success.main,
                  "&:hover": { bgcolor: (theme) => theme.palette.success.main },
                }}
              >
                Add Column
              </Button>
              <CloseIcon
                fontSize="small"
                sx={{
                  color: "white",
                  cursor: "pointer",
                  "&:hover": { color: (theme) => theme.palette.warning.light },
                }}
                onClick={toggleOpenNewColumnForm}
              />
            </Box>
          </Box>
        )}
      </Box>
    </SortableContext>
  )
}

export default ListColumns
