import { getColorHex } from "@/app/theme";
import { useColors } from "@/lib/hooks";
import { Box, StackProps, VStack } from "@chakra-ui/react";
import {
  MouseEvent,
  TransitionEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

export type VResizeProps = {
  topElement: React.ReactNode;
  bottomElement: React.ReactNode;
  startingProportion?: number;
};

const transition = "0.25s height ease";

export default function VResize({
  topElement: leftElement,
  bottomElement: rightElement,
  startingProportion = 0.5,
  ...otherProps
}: VResizeProps & StackProps) {
  const draggableAreaRef = useRef<HTMLDivElement | null>(null);
  const topContainerRef = useRef<HTMLDivElement | null>(null);
  const bottomContainerRef = useRef<HTMLDivElement | null>(null);

  const [dragging, setDragging] = useState(false);
  const [topHeight, setTopHeight] = useState(0);

  const { hover } = useColors();

  useEffect(() => {
    setTopHeight(
      (draggableAreaRef.current?.clientHeight ?? 0) * startingProportion,
    );
  }, [draggableAreaRef]);

  useEffect(() => {
    const cb = () => {
      setDragging(true);
      requestAnimationFrame(() => {
        setDragging(false);
      });
    };
    window.addEventListener("resize", cb);
    return () => {
      window.removeEventListener("resize", cb);
    };
  }, []);

  const getBoundedH = (h: number) =>
    Math.max(0, Math.min(h, draggableAreaRef.current?.clientHeight ?? 0));
  const transitionEnd = (ev: TransitionEvent<HTMLDivElement>) =>
    (ev.currentTarget.style.transition = "none");

  const onMouseMove = useCallback(
    (ev: MouseEvent) => {
      if (dragging) {
        const h = topHeight;
        setTopHeight(getBoundedH(h + ev.movementY));
      }
    },
    [topHeight, dragging],
  );

  return (
    <VStack
      userSelect="none"
      onMouseUp={() => {
        setDragging(false);
      }}
      onMouseMove={onMouseMove}
      cursor={dragging ? "row-resize" : "auto"}
      ref={draggableAreaRef}
      alignItems="center"
      {...otherProps}
      gap={0}
      overflow="hidden"
    >
      <Box
        overflow="hidden"
        ref={topContainerRef}
        h={getBoundedH(topHeight) + "px"}
        w="100%"
        onTransitionEnd={transitionEnd}
      >
        {leftElement}
      </Box>
      <Box
        h="16px"
        alignSelf="stretch"
        cursor="row-resize"
        _hover={{ backgroundColor: hover }}
        onMouseDown={() => setDragging(true)}
        onDoubleClick={() => {
          [topContainerRef, bottomContainerRef].forEach(({ current }) => {
            if (current) {
              current.style.transition = transition;
            }
          });
          const fullH = draggableAreaRef.current?.clientHeight ?? 0;
          const ratio = topHeight / fullH;
          const finalRatio = 1 - ratio;
          const finalW = finalRatio * fullH;
          setTopHeight(finalW);
        }}
        role="group"
        display="flex"
        flexDir="row"
        justifyContent="center"
        alignItems="center"
      >
        <Box
          h="6px"
          w="32px"
          border="1px solid lightgray"
          borderLeft="none"
          borderRight="none"
          _groupHover={{
            borderColor: getColorHex("verde.main"),
          }}
        />
      </Box>
      <Box
        overflow="hidden"
        ref={bottomContainerRef}
        h={
          (draggableAreaRef.current?.clientHeight ?? 0) -
          (getBoundedH(topHeight) + 16) +
          "px"
        }
        w="100%"
        onTransitionEnd={transitionEnd}
      >
        {rightElement}
      </Box>
    </VStack>
  );
}
