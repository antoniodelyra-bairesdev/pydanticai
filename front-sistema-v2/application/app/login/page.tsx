import { pathMetadata } from "../path.metadata";

import LoginCard from "./_components/LoginCard";
import Waves from "./_components/Waves";

export const metadata = pathMetadata["/login"];

export default async function LoginPage() {
  return (
    <div
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <LoginCard />
      <Waves />
    </div>
  );
}
