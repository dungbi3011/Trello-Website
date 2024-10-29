import React from "react";
import { CardIdContext } from "~/utils/NewCardId";
import { mapOrder } from "~/utils/sorts";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import ListItemText from "@mui/material/ListItemText";
import ListItemIcon from "@mui/material/ListItemIcon";
import AddCardIcon from "@mui/icons-material/AddCard";
import EditIcon from "@mui/icons-material/Edit";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Tooltip from "@mui/material/Tooltip";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import DragHandleIcon from "@mui/icons-material/DragHandle";
import ListCards from "./ListCards/ListCards";
import TextField from "@mui/material/TextField";
import CloseIcon from "@mui/icons-material/Close";

function Column({ column, setOrderedColumns, removeColumn, updateColumn }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: column._id,
    data: { ...column },
  });

  const dndKitColumnStyles = {
    touchAction: "none",
    //Nếu sử dụng CSS.transform sẽ bị lỗi sketch về giao diện
    //Sử dụng translate ở đây, ref: https://github.com/clauderic/dnd-kit/issues/117
    transform: CSS.Translate.toString(transform),
    transition,
    height: "100%",
    opacity: isDragging ? 0.5 : undefined,
  };

  //Khởi tạo giá trị cho menu
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);
  //

  //Khởi tạo giá trị lưu trữ các card trong 1 column
  const [orderedCards, setOrderedCards] = React.useState([]);
  React.useEffect(() => {
    if (column?.cards && column?.cardOrderIds) {
      setOrderedCards(mapOrder(column.cards, column.cardOrderIds, "_id"));
    }
  }, [column]);
  //

  //Form tạo card mới
  const [openNewCardForm, setOpenNewCardForm] = React.useState(false);
  const toggleOpenNewCardForm = () => setOpenNewCardForm(!openNewCardForm);
  //

  //Khởi tạo card mới
  const { newCardId, incrementCardId } = React.useContext(CardIdContext);
  const [newCardTitle, setNewCardTitle] = React.useState("");
  const addNewCard = () => {
    if (!newCardTitle) {
      alert("Card title can not be empty!");
      return;
    }
    const newCard = {
      _id: `card-id-${newCardId}`,
      boardId: "board-id-01",
      columnId: column._id,
      title: newCardTitle,
      description: null,
      cover: null,
      memberIds: [],
      comments: [],
      attachments: [],
    };
    setOrderedCards([...column.cards, newCard]);
    //

    // Cập nhật danh sách thẻ trong cùng 1 cột
    const updatedColumn = {
      ...column,
      cards: [...column.cards, newCard],
      cardOrderIds: [...column.cardOrderIds, newCard._id],
    };

    // Update the orderedColumns array
    setOrderedColumns((prevColumns) =>
      prevColumns.map((col) => (col._id === column._id ? updatedColumn : col))
    );

    incrementCardId();
    toggleOpenNewCardForm();
    console.log(newCard);
  };

  //Hàm giúp xóa card - thẻ
  const removeCard = (columnId, cardId) => {
    setOrderedColumns((prevColumns) =>
      prevColumns.map((column) =>
        column._id === columnId
          ? {
              ...column,
              cards: column.cards.filter((card) => card._id !== cardId),
            }
          : column
      )
    );
  };
  //

  //Hàm giúp update, sửa tên card - thẻ
  const updateCard = (columnId, updatedCard) => {
    setOrderedColumns((prevColumns) =>
      prevColumns.map((column) =>
        column._id === columnId
          ? {
              ...column,
              cards: column.cards.map((card) =>
                card._id === updatedCard._id ? updatedCard : card
              ),
            }
          : column
      )
    );
  };

  // Khởi tạo giá trị cho việc update
  const [isEditing, setIsEditing] = React.useState(false);
  const [newTitle, setNewTitle] = React.useState(column.title);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleTitleChange = (e) => {
    setNewTitle(e.target.value);
  };

  const handleTitleSubmit = () => {
    const updatedColumn = { ...column, title: newTitle };
    updateColumn(updatedColumn);
    setOrderedColumns((prevColumns) =>
      prevColumns.map((col) => (col._id === column._id ? updatedColumn : col))
    );
    setIsEditing(false);
  };
  //

  return (
    <div ref={setNodeRef} style={dndKitColumnStyles} {...attributes}>
      <Box
        {...listeners}
        sx={{
          minWidth: "300px",
          maxWidth: "300px",
          bgcolor: (theme) =>
            theme.palette.mode === "dark" ? "#333643" : "#ebecf0",
          ml: 2,
          borderRadius: "6px",
          height: "fit-content",
          maxHeight: (theme) =>
            `calc(${theme.trello.boardContentHeight} - ${theme.spacing(5)})`,
        }}
      >
        {/* {Box Header} */}
        <Box
          sx={{
            height: (theme) => theme.trello.columnHeaderHeight,
            p: 2,
            display: "flex",
            alignItem: "center",
            justifyContent: "space-between",
          }}
        >
          {isEditing ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <TextField
                value={newTitle}
                onChange={handleTitleChange}
                label="Edit column title"
                type="text"
                size="small"
                variant="outlined"
                autoFocus
                inputProps={{
                  maxLength: 28,
                }}
                sx={{
                  "& label": { color: "text.primary" },
                  "& input": {
                    color: (theme) => theme.palette.primary.main,
                    bgcolor: (theme) =>
                      theme.palette.mode === "dark" ? "#333643" : "white",
                  },
                  "& label.Mui-focused": {
                    color: (theme) => theme.palette.primary.main,
                  },
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                      borderColor: (theme) => theme.palette.primary.main,
                    },
                    "&:hover fieldset": {
                      borderColor: (theme) => theme.palette.primary.main,
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: (theme) => theme.palette.primary.main,
                    },
                  },
                  "& .MuiOutlinedInput-input": {
                    borderRadius: 1,
                  },
                }}
              />
              <Button
                onClick={handleTitleSubmit}
                variant="contained"
                size="small"
                color="success"
                sx={{
                  boxShadow: "none",
                  border: "0.5px solid",
                  borderColor: (theme) => theme.palette.success.main,
                  "&:hover": {
                    bgcolor: (theme) => theme.palette.success.main,
                  },
                  gap: 1,
                }}
              >
                Save
              </Button>
            </Box>
          ) : (
            <Typography
              variant="h6"
              sx={{ fontSize: "1rem", fontWeight: "bold", cursor: "pointer" }}
            >
              {column.title}
            </Typography>
          )}
          <Box>
            <Tooltip title="More options">
              <ExpandMoreIcon
                sx={{
                  color: "text.primary",
                  cursor: "pointer",
                }}
                id="basic-column-dropdown"
                aria-controls={open ? "basic-menu-column-dropdown" : undefined}
                aria-haspopup="true"
                aria-expanded={open ? "true" : undefined}
                onClick={handleClick}
              />
            </Tooltip>
            <Menu
              id="basic-menu-column-dropdown"
              anchorEl={anchorEl}
              open={open}
              onClose={handleClose}
              MenuListProps={{
                "aria-labelledby": "basic-column-dropdown",
              }}
            >
              <MenuItem onClick={() => removeColumn(column._id)}>
                <ListItemIcon>
                  <DeleteForeverIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Remove this column</ListItemText>
              </MenuItem>
              <MenuItem onClick={handleEditClick}>
                <ListItemIcon>
                  <EditIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Edit this column</ListItemText>
              </MenuItem>
            </Menu>
          </Box>
        </Box>
        {/* {Box List Card} */}
        <ListCards
          cards={orderedCards}
          removeCard={removeCard}
          updateCard={updateCard}
          columnID={column._id}
        />
        {/* {Box Footer} */}
        <Box
          sx={{
            height: (theme) => theme.trello.columnFooterHeight,
            p: 2,
          }}
        >
          {!openNewCardForm ? (
            <Box
              sx={{
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <Button
                startIcon={<AddCardIcon />}
                onClick={toggleOpenNewCardForm}
              >
                Add new card
              </Button>
              <Tooltip title="Drag to move">
                <DragHandleIcon sx={{ cursor: "pointer" }} />
              </Tooltip>
            </Box>
          ) : (
            <Box
              sx={{
                height: "100%",
                display: "flex",
                alignItems: "center",
                gap: 1,
              }}
            >
              <TextField
                label="Enter card title"
                type="text"
                size="small"
                variant="outlined"
                autoFocus
                value={newCardTitle}
                onChange={(e) => setNewCardTitle(e.target.value)}
                sx={{
                  "& label": { color: "text.primary" },
                  "& input": {
                    color: (theme) => theme.palette.primary.main,
                    bgcolor: (theme) =>
                      theme.palette.mode === "dark" ? "#333643" : "white",
                  },
                  "& label.Mui-focused": {
                    color: (theme) => theme.palette.primary.main,
                  },
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                      borderColor: (theme) => theme.palette.primary.main,
                    },
                    "&:hover fieldset": {
                      borderColor: (theme) => theme.palette.primary.main,
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: (theme) => theme.palette.primary.main,
                    },
                  },
                  "& .MuiOutlinedInput-input": {
                    borderRadius: 1,
                  },
                }}
              />
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Button
                  onClick={addNewCard}
                  variant="contained"
                  color="success"
                  size="small"
                  sx={{
                    boxShadow: "none",
                    border: "0.5px solid",
                    borderColor: (theme) => theme.palette.success.main,
                    "&:hover": {
                      bgcolor: (theme) => theme.palette.success.main,
                    },
                  }}
                >
                  Add
                </Button>
                <CloseIcon
                  fontSize="small"
                  sx={{
                    color: (theme) => theme.palette.warning.light,
                    cursor: "pointer",
                  }}
                  onClick={toggleOpenNewCardForm}
                />
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    </div>
  );
}

export default Column;
