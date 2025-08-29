import React, { CSSProperties } from "react";

export default function SSRFlex({
  flexDirection = "row",
  children,
  ...props
}: CSSProperties & { children?: React.ReactNode }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection,
        ...props,
      }}
    >
      {children}
    </div>
  );
}
