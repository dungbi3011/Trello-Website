import React, { useCallback } from "react";
import axios from "axios";
import Box from "@mui/material/Box";
import ListColumns from "./ListColumns/ListColumns";
import { mapOrder } from "~/utils/sorts";
import { generatePlaceHolderCard } from "~/utils/formatters";

import {
  DndContext,
  useSensor,
  useSensors,
  MouseSensor,
  TouchSensor,
  DragOverlay,
  defaultDropAnimationSideEffects,
  closestCorners,
  pointerWithin,
  getFirstCollision,
} from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import { cloneDeep, isEmpty } from "lodash";

import Column from "./ListColumns/Column/Column";
import Card from "./ListColumns/Column/ListCards/Card/Card";

const ACTIVE_DRAG_ITEM_TYPE = {
  COLUMN: "ACTIVE_DRAG_ITEM_TYPE_COLUMN",
  CARD: "ATIVE_DRAG_ITEM_TYPE_CARD",
};

function BoardContent({ board }) {
  // Trỏ chuột di chuyển 10px thì kéo được cột
  // const pointerSensor = useSensor(PointerSensor, { activationConstraint: { distance: 10 } })

  // Chuột di chuyển 10px thì kéo được cột
  const mouseSensor = useSensor(MouseSensor, {
    activationConstraint: { distance: 10 },
  });

  // Nhấn giữ 250ms và di chuyển 500px thì kéo được cột
  const touchSensor = useSensor(TouchSensor, {
    activationConstraint: { delay: 250, tolerance: 500 },
  });

  // const mySensors = useSensors(pointerSensor)
  const mySensors = useSensors(mouseSensor, touchSensor);

  const [orderedColumns, setOrderedColumns] = React.useState(
    mapOrder(board?.columns, board?.columnOrderIds, "_id")
  );

  //Chỉ một card được kéo thả trong cùng 1 thời điểm
  const [activeDragItemId, setActiveDragItemId] = React.useState(null);
  const [activeDragItemType, setActiveDragItemType] = React.useState(null);
  const [activeDragItemData, setActiveDragItemData] = React.useState(null);
  const [oldColumnWhenDraggingCard, setOldColumnWhenDraggingCard] =
    React.useState(null);

  //Điểm va chạm cuối cùng (xử lý thuật toán phát hiện va chạm)
  const lastOverId = React.useRef(null);

  //Tìm 1 column theo CardId
  const findColumnByCardId = (cardId) => {
    return orderedColumns.find((column) =>
      column.cards.map((card) => card._id)?.includes(cardId)
    );
  };

  //Function cập nhật lại state khi di chuyển các card trong cùng 1 column
  const moveCardsInColumn = async (
    overColumn,
    activeDragItemId,
    overCardId
  ) => {
    // Get the old and new positions for the card within the column
    const oldCardIndex = overColumn?.cards?.findIndex(
      (c) => c._id === activeDragItemId
    );
    const newCardIndex = overColumn?.cards?.findIndex(
      (c) => c._id === overCardId
    );

    // Reorder cards using arrayMove utility
    const reorderedCards = arrayMove(
      overColumn?.cards,
      oldCardIndex,
      newCardIndex
    );

    // Update state with new card order
    setOrderedColumns((prevColumns) => {
      const nextColumns = cloneDeep(prevColumns);
      const targetColumn = nextColumns.find(
        (column) => column._id === overColumn._id
      );

      targetColumn.cards = reorderedCards;
      targetColumn.cardOrderIds = reorderedCards.map((card) => card._id);

      return nextColumns;
    });

    // Send updated order to back-end
    try {
      const response = await axios.patch(
        `http://127.0.0.1:5000//boards/${board._id}/columns/${overColumn._id}/cards/move`,
        { cardOrderIds: reorderedCards.map((card) => card._id) }
      );
      console.log("Reorder update:", response.data);
    } catch (error) {
      console.error("Error updating card order:", error);
    }
  };

  //Function cập nhật lại state khi di chuyển Card giữa các cột khác nhau
  const moveCardBetweenDifferentColumns = async (
    overColumn,
    overCardId,
    active,
    over,
    activeColumn,
    activeDraggingCardId,
    activeDraggingCardData
  ) => {
    setOrderedColumns((prevColumns) => {
      const overCardIndex = overColumn?.cards?.findIndex(
        (card) => card._id === overCardId
      );

      let newCardIndex;
      const isBelowOverItem =
        active.rect.current.translated &&
        active.rect.current.translated.top > over.rect.top + over.rect.height;
      const modifier = isBelowOverItem ? 1 : 0;
      newCardIndex =
        overCardIndex >= 0
          ? overCardIndex + modifier
          : overColumn?.cards?.length + 1;

      const nextColumns = cloneDeep(prevColumns);
      const nextActiveColumn = nextColumns.find(
        (column) => column._id === activeColumn._id
      );
      const nextOverColumn = nextColumns.find(
        (column) => column._id === overColumn._id
      );

      if (nextActiveColumn) {
        nextActiveColumn.cards = nextActiveColumn.cards.filter(
          (card) => card._id !== activeDraggingCardId
        );

        if (isEmpty(nextActiveColumn.cards)) {
          nextActiveColumn.cards = [generatePlaceHolderCard(nextActiveColumn)];
        }

        nextActiveColumn.cardOrderIds = nextActiveColumn.cards.map(
          (card) => card._id
        );
      }

      if (nextOverColumn) {
        nextOverColumn.cards = nextOverColumn.cards.filter(
          (card) => card._id !== activeDraggingCardId
        );

        const rebuild_activeDraggingCardData = {
          ...activeDraggingCardData,
          columnId: nextOverColumn._id,
        };

        nextOverColumn.cards = nextOverColumn.cards.toSpliced(
          newCardIndex,
          0,
          rebuild_activeDraggingCardData
        );

        nextOverColumn.cards = nextOverColumn.cards.filter(
          (card) => !card.FE_PlaceholderCard
        );

        nextOverColumn.cardOrderIds = nextOverColumn.cards.map(
          (card) => card._id
        );
      }

      //API calls
      axios
        .patch(
          `http://127.0.0.1:5000/boards/${board._id}/columns/${activeColumn._id}/cards/${activeDraggingCardId}/move`,
          {
            activeCardOrderIds: nextActiveColumn.cardOrderIds,
            overCardOrderIds: nextOverColumn.cardOrderIds,
            toColumnId: overColumn._id,
            newCardIndex: newCardIndex,
          }
        )
        .then((response) => {
          console.log(response.data.message);
        })
        .catch((error) => {
          console.error("Error moving card:", error);
        });

      return nextColumns;
    });
  };

  //Trigger khi bắt đầu kéo 1 phần tử
  const handleDragStart = (event) => {
    setActiveDragItemId(event?.active?.id);
    setActiveDragItemType(
      event?.active?.data?.current?.columnId
        ? ACTIVE_DRAG_ITEM_TYPE.CARD
        : ACTIVE_DRAG_ITEM_TYPE.COLUMN
    );
    setActiveDragItemData(event?.active?.data?.current);

    if (event?.active?.data?.current?.columnId) {
      setOldColumnWhenDraggingCard(findColumnByCardId(event?.active?.id));
    }
  };

  //Trigger khi đang kéo 1 phần tử
  const handleDragOver = (event) => {
    //Ko làm gì cả, nếu đang trong quá trình thực hiện kéo thả
    if (activeDragItemType === ACTIVE_DRAG_ITEM_TYPE.COLUMN) return;

    //Nếu kéo card thì xử lý thêm để có thể kéo card qua lại giữa các column
    const { active, over } = event;

    //Ko làm gì cả, nếu ko tồn tại active, over
    if (!active || !over) return;

    const {
      id: activeDraggingCardId,
      data: { current: activeDraggingCardData },
    } = active;
    const { id: overCardId } = over;

    //Tìm 2 column theo CardId
    const activeColumn = findColumnByCardId(activeDraggingCardId);
    const overColumn = findColumnByCardId(overCardId);

    //Ko làm gì cả, nếu 1 trong 2 ko tồn tại
    if (!activeColumn || !overColumn) return;

    if (activeColumn._id != overColumn._id) {
      moveCardBetweenDifferentColumns(
        overColumn,
        overCardId,
        active,
        over,
        activeColumn,
        activeDraggingCardId,
        activeDraggingCardData
      );
    }
  };

  //Trigger khi kết thúc kéo 1 phần tử (thả)
  const handleDragEnd = (event) => {
    // console.log('handleDragEnd: ', event)
    const { active, over } = event;

    // Nếu over ko tồn tại thì return (khi k xác định dc vị trí kéo đến)
    if (!active || !over) return;

    //Xu ly keo tha Card
    if (activeDragItemType === ACTIVE_DRAG_ITEM_TYPE.CARD) {
      const {
        id: activeDraggingCardId,
        data: { current: activeDraggingCardData },
      } = active;
      const { id: overCardId } = over;

      //Tìm 2 column theo CardId
      const activeColumn = findColumnByCardId(activeDraggingCardId);
      const overColumn = findColumnByCardId(overCardId);

      //Ko làm gì cả, nếu 1 trong 2 ko tồn tại
      if (!activeColumn || !overColumn) return;

      if (oldColumnWhenDraggingCard._id !== overColumn._id) {
        //Di chuyển card khác cột
        moveCardBetweenDifferentColumns(
          overColumn,
          overCardId,
          active,
          over,
          activeColumn,
          activeDraggingCardId,
          activeDraggingCardData
        );
      } else {
        // Di chuyển card cùng 1 cột
        moveCardsInColumn(overColumn, activeDragItemId, overCardId);
      }
    }

    const handleColumnDrag = async (
      activeDragItemType,
      active,
      over,
      orderedColumns,
      setOrderedColumns,
      setActiveDragItemId,
      setActiveDragItemType,
      setActiveDragItemData,
      setOldColumnWhenDraggingCard
    ) => {
      if (activeDragItemType === ACTIVE_DRAG_ITEM_TYPE.COLUMN) {
        if (active.id !== over.id) {
          // Find old and new index positions
          const oldColumnIndex = orderedColumns.findIndex(
            (c) => c._id === active.id
          );
          const newColumnIndex = orderedColumns.findIndex(
            (c) => c._id === over.id
          );

          // Reorder columns array
          const dndOrderedColumns = arrayMove(
            orderedColumns,
            oldColumnIndex,
            newColumnIndex
          );
          const dndOrderedColumnsIds = dndOrderedColumns.map((c) => c._id);

          // Update state for UI
          setOrderedColumns(dndOrderedColumns);

          // API call to update column order in the back-end
          try {
            const response = await axios.patch(
              `http://127.0.0.1:5000/boards/${board._id}/columns/move`,
              { columnOrderIds: dndOrderedColumnsIds }
            );
            console.log("Column order updated:", response.data.message);
          } catch (error) {
            console.error("Error updating column order:", error);
          }
        }
      }

      // Reset drag states
      setActiveDragItemId(null);
      setActiveDragItemType(null);
      setActiveDragItemData(null);
      setOldColumnWhenDraggingCard(null);
    };

    handleColumnDrag(
      activeDragItemType,
      active,
      over,
      orderedColumns,
      setOrderedColumns,
      setActiveDragItemId,
      setActiveDragItemType,
      setActiveDragItemData,
      setOldColumnWhenDraggingCard
    );
  };

  const isOverlapping = (rect1, rect2) => {
    return !(
      rect1.right < rect2.left ||
      rect1.left > rect2.right ||
      rect1.bottom < rect2.top ||
      rect1.top > rect2.bottom
    );
  };

  const myDropAnimation = {
    sideEffects: defaultDropAnimationSideEffects({
      styles: { active: { opacity: "0.5" } },
    }),
  };

  const collisionDetectionStrategy = useCallback(
    (args) => {
      if (activeDragItemType === ACTIVE_DRAG_ITEM_TYPE.COLUMN) {
        return closestCorners({ ...args });
      }

      //Tìm các điểm giao nhau, va chạm với con trỏ chuột
      const pointerIntersections = pointerWithin(args);

      if (!pointerIntersections?.length) return [];

      //Thuật toán trả về mảng chứa các va chạm
      // const intersections = !!pointerIntersections?.length
      // ? pointerIntersections
      // : rectIntersection(args)

      //Tìm overId đầu tiên trong đám intersections trên
      let overId = getFirstCollision(pointerIntersections, "id");
      if (overId) {
        const checkColumn = orderedColumns.find(
          (column) => column._id === overId
        );
        if (checkColumn) {
          overId = closestCorners({
            ...args,
            droppableContainers: args.droppableContainers.filter(
              (container) => {
                return (
                  container.id !== overId &&
                  checkColumn?.cardOrderIds?.includes(container.id)
                );
              }
            ),
          })[0]?.id;
        }

        lastOverId.current = overId;
        return [{ id: overId }];
      }

      return lastOverId.current ? [{ id: lastOverId.current }] : [];
    },
    [activeDragItemType]
  );

  return (
    <DndContext
      sensors={mySensors}
      // collisionDetection={closestCorners}
      collisionDetection={collisionDetectionStrategy}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <Box
        sx={{
          backgroundImage: (theme) =>
            theme.palette.mode === "dark"
              ? "linear-gradient(130deg, hsl(215, 90%, 35%), #099BC7)"
              : "linear-gradient(160deg, hsl(215, 90%, 50%), #54D8FF)",
          width: "100%",
          height: (theme) => theme.trello.boardContentHeight,
          p: "10px 0",
        }}
      >
        <ListColumns
          boardID={board._id}
          columns={orderedColumns}
          setOrderedColumns={setOrderedColumns}
        />
        <DragOverlay dropAnimation={myDropAnimation}>
          {!activeDragItemType && null}
          {activeDragItemType === ACTIVE_DRAG_ITEM_TYPE.COLUMN && (
            <Column column={activeDragItemData} />
          )}
          {activeDragItemType === ACTIVE_DRAG_ITEM_TYPE.CARD && (
            <Card card={activeDragItemData} />
          )}
        </DragOverlay>
      </Box>
    </DndContext>
  );
}

export default BoardContent;