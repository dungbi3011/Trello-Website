import React from "react";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { Card as MuiCard } from "@mui/material";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import GroupIcon from "@mui/icons-material/Group";
import CommentIcon from "@mui/icons-material/Comment";
import AttachmentIcon from "@mui/icons-material/Attachment";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";
import Tooltip from "@mui/material/Tooltip";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import EditIcon from "@mui/icons-material/Edit";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

function Card({ card, removeCard, columnId }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: card._id,
    data: { ...card },
  });

  const dndKitCardStyles = {
    touchAction: "none",
    //Nếu sử dụng CSS.transform sẽ bị lỗi sketch về giao diện
    //Sử dụng translate ở đây, ref: https://github.com/clauderic/dnd-kit/issues/117
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : undefined,
    border: isDragging ? "1px solid #2ecc71" : undefined,
  };

  const shouldShowCardActions = () => {
    return (
      !!card?.membersIds?.length ||
      !!card?.comments?.length ||
      !!card?.attachments?.length
    );
  };

  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  return (
    <>
      <Tooltip title="More options">
        <MuiCard
          ref={setNodeRef}
          style={dndKitCardStyles}
          {...attributes}
          {...listeners}
          sx={{
            cursor: "pointer",
            boxShadow: "0 1px 1px rgba(0, 0, 0, 0.2)",
            overflow: "unset",
            display: card?.FE_PlaceholderCard ? "none" : "block",
            justifyContent: "space-between",
            border: "1px solid transparent",
            "&:hover": { borderColor: (theme) => theme.palette.primary.main },  
          }}
          onClick={handleClick}
        >
          {card?.cover && (
            <CardMedia sx={{ height: 140 }} image={card?.cover} />
          )}

          <CardContent sx={{ p: 1.5, "&:last-child": { p: 1.5 } }}>
            <Typography>{card?.title}</Typography>
          </CardContent>
          {shouldShowCardActions() && (
            <CardActions sx={{ p: "0 4px 8px 4px " }}>
              {!!card?.memberIds?.length && (
                <Button size="small" startIcon={<GroupIcon />}>
                  {card?.memberIds?.length}
                </Button>
              )}
              {!!card?.comments?.length && (
                <Button size="small" startIcon={<CommentIcon />}>
                  {card?.comments?.length}
                </Button>
              )}
              {!!card?.attachments?.length && (
                <Button size="small" startIcon={<AttachmentIcon />}>
                  {card?.attachments?.length}
                </Button>
              )}
            </CardActions>
          )}
        </MuiCard>
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
        <MenuItem onClick={() => removeCard(columnId, card._id)}>
          <ListItemIcon>
            <DeleteForeverIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Remove this card</ListItemText>
        </MenuItem>
        <MenuItem>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit this card</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
}

export default Card;
