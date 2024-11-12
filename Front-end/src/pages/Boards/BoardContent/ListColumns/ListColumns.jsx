import React from "react";
import Box from "@mui/material/Box";
import Column from "./Column/Column";
import Button from "@mui/material/Button";
import NoteAddIcon from "@mui/icons-material/NoteAdd";
import TextField from "@mui/material/TextField";
import CloseIcon from "@mui/icons-material/Close";
import {
  SortableContext,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";

function ListColumns({ boardID, columns, setOrderedColumns }) {
  const [openNewColumnForm, setOpenNewColumnForm] = React.useState(false);
  const toggleOpenNewColumnForm = () =>
    setOpenNewColumnForm(!openNewColumnForm);

  const [newColumnTitle, setNewColumnTitle] = React.useState("");
  const [newColumnId, setNewColumnId] = React.useState(5);

  const addNewColumn = async () => {
    const boardId = boardID; // Define boardId directly

    if (!newColumnTitle) {
      alert("Column title can not be empty!");
      return;
    }
    const newColumn = {
      title: newColumnTitle,
    };

    try {
      const response = await fetch(
        `http://127.0.0.1:5000/boards/${boardId}/columns`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newColumn),
        }
      );
      const data = await response.json();
      setOrderedColumns([...columns, data]);
      toggleOpenNewColumnForm();
      setNewColumnId(newColumnId + 1);
    } catch (error) {
      console.error("Error creating column:", error);
    }
  };

  const removeColumn = async (columnID) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/boards/${boardID}/columns/${columnID}`,
        {
          method: "DELETE",
        }
      );
  
      if (!response.ok) {
        throw new Error("Failed to delete column");
      }
  
      // Remove column from local state if deletion was successful
      setOrderedColumns(columns.filter((column) => column._id !== columnID));
      console.log(`Column ${columnID} removed successfully`);
    } catch (error) {
      console.error("Error deleting column:", error);
    }
  };

  const updateColumn = async (updatedColumn) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/boards/${boardID}/columns/${updatedColumn._id}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(updatedColumn),
        }
      );
  
      if (!response.ok) {
        throw new Error("Failed to update column");
      }
  
      const data = await response.json();
  
      // Update the column in the local state
      setOrderedColumns(
        columns.map((column) => (column._id === updatedColumn._id ? data : column))
      );
      console.log(`Column ${updatedColumn._id} updated successfully`);
    } catch (error) {
      console.error("Error updating column:", error);
    }
  };

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
          <Column
            key={column._id}
            boardID={boardID}
            column={column}
            setOrderedColumns={setOrderedColumns}
            removeColumn={removeColumn}
            updateColumn={updateColumn}
          />
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
  );
}

export default ListColumns;