"use client";

import { getColorHex } from "@/app/theme";
import { useColors } from "@/lib/hooks";
import { strCSSColor } from "@/lib/util/string";
import { SmallCloseIcon } from "@chakra-ui/icons";
import {
  Button,
  HStack,
  LightMode,
  Tag,
  TagCloseButton,
  TagLabel,
  Text,
  VStack,
} from "@chakra-ui/react";
import { ChangeEventHandler, KeyboardEvent, useEffect, useState } from "react";
import TextInput from "./TextInput";

export type TagInputProps = {
  onTagsChanged?: (tags: string[]) => void;
  onValueChanged?: (value: string) => void;
  forbidden?: string[];
  forbiddenMsg?: string;
};

export default function TagInput({
  onTagsChanged,
  onValueChanged,
  forbidden = [],
  forbiddenMsg = "Valores não permitidos:",
}: TagInputProps) {
  const [value, setValue] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [forbiddenTags, setForbiddenTags] = useState<string[]>([]);

  const forbiddenSet = new Set(forbidden);

  const setUniqueTags = (tags: string[]) => {
    const uniqueTags = [...new Set(tags.map((tag) => tag.trim()))];
    const cantInsert: string[] = [];
    const withoutForbiddenTags = uniqueTags.filter((tag) => {
      if (!forbiddenSet.has(tag)) return true;
      cantInsert.push(tag);
    });
    setTags(withoutForbiddenTags);
    setForbiddenTags([...new Set([...forbiddenTags, ...cantInsert])]);
  };
  const enter = (value: string, tags: string[]) => {
    setValue(value);
    setUniqueTags(tags);
  };
  const handleChange: ChangeEventHandler<HTMLInputElement> = ({
    target: { value },
  }) => {
    const newTags = value.split(/( |\t|\n)/).filter((v) => v.trim());

    if (newTags.length != 1) {
      enter("", [...tags, ...newTags]);
      return;
    }

    const endsWithSpace = value.endsWith(" ");
    if (!endsWithSpace) {
      setValue(value);
      return;
    }
    enter("", [...tags, value]);
  };
  const handleKbEvents = (ev: KeyboardEvent<HTMLInputElement>) => {
    if (ev.key == "Enter" && value.trim()) {
      enter("", [...tags, value]);
    }
    if (ev.key == "Backspace" && !value.trim() && tags.length) {
      ev.preventDefault();
      enter(tags.splice(tags.length - 1, 1)[0], tags);
    }
  };
  const handleDelete = (position: number) => {
    tags.splice(position, 1);
    setUniqueTags(tags);
  };
  const handleTagClick = (position: number) => {
    if (value) return;

    const [clickedValue] = tags.splice(position, 1);
    enter(clickedValue, tags);
  };
  const handleForbbidenTagClick = (position: number) => {
    if (value) return;

    const [clickedValue] = forbiddenTags.splice(position, 1);
    setValue(clickedValue);
    setForbiddenTags(forbiddenTags);
  };

  useEffect(() => {
    onTagsChanged?.(tags);
  }, [tags]);

  useEffect(() => {
    onValueChanged?.(value);
  }, [value]);

  const { hover, bgError, text } = useColors();

  return (
    <HStack wrap="wrap">
      {tags
        .map((tag, i) => (
          <Tag key={i} borderRadius="full" variant="solid" bgColor="#7F7F7F1F">
            <TagLabel
              userSelect="none"
              cursor={value ? "not-allowed" : "pointer"}
              color={strCSSColor(tag)}
              onClick={() => handleTagClick(i)}
            >
              {tag}
            </TagLabel>
            <TagCloseButton onClick={() => handleDelete(i)} />
          </Tag>
        ))
        .sort()}
      <HStack w="100%" gap={0}>
        <TextInput
          placeholder="Insira aqui os códigos..."
          key="input"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKbEvents}
        />
        <LightMode>
          <Button
            onClick={(ev) => enter("", [...tags, value])}
            borderTopLeftRadius={0}
            borderBottomLeftRadius={0}
            colorScheme="verde"
            size="sm"
            isDisabled={!value}
          >
            →
          </Button>
        </LightMode>
      </HStack>
      {forbiddenTags.length && (
        <VStack alignItems="flex-start">
          <HStack mt="8px">
            <VStack
              justify="center"
              w="16px"
              h="16px"
              cursor="pointer"
              bgColor={hover}
              _hover={{ bgColor: getColorHex("cinza.main") + "7F" }}
              borderRadius="full"
              onClick={() => setForbiddenTags([])}
            >
              <SmallCloseIcon opacity={0.7} boxSize="14px" />
            </VStack>
            <Text fontSize="sm" color="rosa.main">
              {forbiddenMsg}
            </Text>
          </HStack>
          <HStack wrap="wrap" gap="2px">
            {forbiddenTags
              .map((tag, i) => (
                <Tag
                  key={i}
                  p="4px"
                  borderRadius="full"
                  variant="solid"
                  bgColor={getColorHex(bgError) + "3F"}
                >
                  <TagLabel
                    color={text}
                    opacity={0.6}
                    fontSize="xs"
                    userSelect="none"
                    cursor={value ? "not-allowed" : "pointer"}
                    onClick={() => handleForbbidenTagClick(i)}
                  >
                    {tag}
                  </TagLabel>
                </Tag>
              ))
              .sort()}
          </HStack>
        </VStack>
      )}
    </HStack>
  );
}
