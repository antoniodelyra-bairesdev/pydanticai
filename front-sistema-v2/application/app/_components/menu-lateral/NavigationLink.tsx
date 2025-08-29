"use client";

import { useColors } from "@/lib/hooks";
import { Box } from "@chakra-ui/react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export type NavigationLinkProps = {
  href: string;
  text: string;
  onClick?: () => void;
};

export default function NavigationLink({
  href,
  text,
  onClick = () => {},
}: NavigationLinkProps) {
  const pathname = usePathname();
  const {
    blue: azulContraste,
    blueHover: azulContrasteHover,
    textOption,
    hover,
  } = useColors();
  const selected = href === "/" ? href === pathname : pathname.startsWith(href);

  return (
    <Link onClick={onClick} href={href}>
      <Box
        position="relative"
        bgColor={selected ? azulContraste : "transparent"}
        color={selected ? "white" : textOption}
        p="8px 24px"
        _hover={{
          bgColor: selected ? azulContrasteHover : hover,
        }}
        transition="0.25s all"
        role="group"
      >
        <Box
          position="absolute"
          width={selected ? "8px" : "0px"}
          _groupHover={{
            width: "8px",
          }}
          height="100%"
          top={0}
          left={0}
          bgColor="verde.main"
          transition="0.25s all"
        />
        {text}
      </Box>
    </Link>
  );
}
