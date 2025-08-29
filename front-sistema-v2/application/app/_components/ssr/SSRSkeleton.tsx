import { CSSProperties } from "react";
import "./SSRSkeleton.css";

export default function SSRSkeleton({
  startBackgroundColor = "#E6E7E8FF",
  endBackgroundColor = "#E6E7E800",
  ...props
}: CSSProperties & {
  startBackgroundColor?: string;
  endBackgroundColor?: string;
}) {
  const style = {
    "--color-start": startBackgroundColor,
    "--color-end": endBackgroundColor,
    width: "100%",
    height: "100%",
    borderRadius: "8px",
    animation: "0.8s linear infinite alternate ssr-skeleton",
    ...props,
  };
  return <div style={style} />;
}
