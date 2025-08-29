import SSRFlex from "@/app/_components/ssr/SSRFlex";
import SSRSkeleton from "@/app/_components/ssr/SSRSkeleton";

export default function CalculadoraLoading() {
  return (
    <SSRFlex flexDirection="column" gap="8px" width="100vw" height="100vh">
      {Array(10)
        .fill(null)
        .map((_, i) => (
          <SSRSkeleton key={i} width="256px" height="32px" />
        ))}
    </SSRFlex>
  );
}
