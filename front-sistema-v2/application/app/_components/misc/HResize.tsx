import { getColorHex } from "@/app/theme";
import { useColors } from "@/lib/hooks";
import { Box, HStack, StackProps } from "@chakra-ui/react";
import { TransitionEvent, useEffect, useRef, useState } from "react";

export type HResizeProps = {
  leftElement: React.ReactNode;
  rightElement: React.ReactNode;
  startingProportion?: number;
  startingLeftWidth?: number;
};

const transition = "0.25s width ease";

export default function HResize({
  leftElement,
  rightElement,
  startingProportion = 0.825,
  startingLeftWidth,
  ...otherProps
}: HResizeProps & StackProps) {
  const draggableAreaRef = useRef<HTMLDivElement | null>(null);
  const leftContainerRef = useRef<HTMLDivElement | null>(null);
  const rightContainerRef = useRef<HTMLDivElement | null>(null);

  const [dragging, setDragging] = useState(false);
  const [leftWidth, setLeftWidth] = useState(startingLeftWidth ?? 0);

  const { hover } = useColors();

  useEffect(() => {
    setLeftWidth(
      startingLeftWidth ??
        (draggableAreaRef.current?.clientWidth ?? 0) * startingProportion,
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

  const getBoundedW = (w: number) => {
    if (!draggableAreaRef.current?.clientWidth) {
      return Math.max(0, w);
    }

    return Math.max(0, Math.min(w, draggableAreaRef.current?.clientWidth));
  };

  const transitionEnd = (ev: TransitionEvent<HTMLDivElement>) =>
    (ev.currentTarget.style.transition = "none");

  return (
    <HStack
      userSelect="none"
      onMouseUp={() => {
        setDragging(false);
      }}
      onMouseMove={(ev) => {
        if (dragging) {
          const w = leftWidth;
          setLeftWidth(getBoundedW(w + ev.movementX));
        }
      }}
      cursor={dragging ? "col-resize" : "auto"}
      ref={draggableAreaRef}
      alignItems="center"
      {...otherProps}
      gap={0}
      overflow="hidden"
    >
      <Box
        ref={leftContainerRef}
        w={getBoundedW(leftWidth) + "px"}
        h="100%"
        onTransitionEnd={transitionEnd}
        overflow="auto"
      >
        {leftElement}
      </Box>
      <Box
        w="16px"
        alignSelf="stretch"
        cursor="col-resize"
        _hover={{ backgroundColor: hover }}
        onMouseDown={() => setDragging(true)}
        onDoubleClick={() => {
          [leftContainerRef, rightContainerRef].forEach(({ current }) => {
            if (current) {
              current.style.transition = transition;
            }
          });
          const fullW = draggableAreaRef.current?.clientWidth ?? 0;
          const ratio = leftWidth / fullW;
          const finalRatio = 1 - ratio;
          const finalW = finalRatio * fullW;
          setLeftWidth(finalW);
        }}
        role="group"
        display="flex"
        flexDir="column"
        justifyContent="center"
        alignItems="center"
      >
        <Box
          w="6px"
          h="32px"
          border="1px solid lightgray"
          borderTop="none"
          borderBottom="none"
          _groupHover={{
            borderColor: getColorHex("verde.main"),
          }}
        />
      </Box>
      <Box
        ref={rightContainerRef}
        w={
          (draggableAreaRef.current?.clientWidth ?? 0) -
          (getBoundedW(leftWidth) + 16) +
          "px"
        }
        h="100%"
        onTransitionEnd={transitionEnd}
        overflow="auto"
      >
        {rightElement}
      </Box>
    </HStack>
  );
}
