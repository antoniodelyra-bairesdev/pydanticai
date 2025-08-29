import {
  HStack,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  RangeSlider,
  RangeSliderFilledTrack,
  RangeSliderThumb,
  RangeSliderTrack,
  VStack,
} from "@chakra-ui/react";

export type RangeInputProps = {
  min: number;
  max: number;
  step: number;
  onLChange?: (valueAsString: string, valueAsNumber: number) => void;
  lValue?: number;
  onRChange?: (valueAsString: string, valueAsNumber: number) => void;
  rValue?: number;
  isDisabled?: boolean;
};

export default function RangeInput({
  min,
  max,
  step,
  isDisabled,
  onLChange,
  lValue,
  onRChange,
  rValue,
}: RangeInputProps) {
  min = Math.min(min, max);
  max = Math.max(min, max);
  return (
    <HStack
      alignItems="stretch"
      border="1px solid"
      borderColor="cinza.main"
      borderRadius="8px"
      gap={0}
    >
      <NumberInput
        borderColor="transparent"
        w="84px"
        allowMouseWheel
        isDisabled={isDisabled}
        focusBorderColor="verde.main"
        size="xs"
        defaultValue={min}
        min={min}
        max={max}
        step={step}
        keepWithinRange={true}
        clampValueOnBlur={true}
        onChange={onLChange}
        value={lValue}
      >
        <NumberInputField />
        <NumberInputStepper>
          <NumberIncrementStepper />
          <NumberDecrementStepper />
        </NumberInputStepper>
      </NumberInput>
      <VStack
        borderLeft="1px solid lightgray"
        minW="240px"
        pl="16px"
        pr="16px"
        justifyContent="center"
      >
        <RangeSlider
          size="sm"
          defaultValue={[min, max]}
          min={min}
          max={max}
          step={step}
          value={[
            lValue === undefined || isNaN(lValue) ? 1 : lValue,
            rValue === undefined || isNaN(rValue) ? 1 : rValue,
          ]}
          onChange={([l, r]) => {
            if (lValue !== l) {
              onLChange?.(String(l), l);
            }
            if (rValue !== r) {
              onRChange?.(String(r), r);
            }
          }}
        >
          <RangeSliderTrack bg="verde.100">
            <RangeSliderFilledTrack bg="verde.main" />
          </RangeSliderTrack>
          <RangeSliderThumb bgColor="azul_4.main" boxSize="16px" index={0} />
          <RangeSliderThumb bgColor="azul_4.main" boxSize="16px" index={1} />
        </RangeSlider>
      </VStack>
      <NumberInput
        w="84px"
        allowMouseWheel
        isDisabled={max === 1}
        focusBorderColor="verde.main"
        size="xs"
        defaultValue={1}
        min={min}
        max={max}
        step={step}
        keepWithinRange={true}
        clampValueOnBlur={true}
        onChange={onRChange}
        value={rValue}
      >
        <NumberInputField />
        <NumberInputStepper>
          <NumberIncrementStepper />
          <NumberDecrementStepper />
        </NumberInputStepper>
      </NumberInput>
    </HStack>
  );
}
