import Hint from "@/app/_components/texto/Hint";
import { FormControl, FormLabel, Text } from "@chakra-ui/react";
import { Field, FieldInputProps, FieldProps, FormikProps } from "formik";
import { Children, ReactNode, cloneElement, isValidElement } from "react";

type FormFieldProps = {
  field: string;
  label: string | ReactNode;
  form: FormikProps<any>;
  required?: boolean;
  children: ((fieldInfo: FieldInputProps<any>) => JSX.Element) | ReactNode;
};

export default function FormField({
  field,
  label,
  form: { errors, touched },
  required,
  children,
}: FormFieldProps) {
  const inputs = (fieldInfo: FieldInputProps<any>) => {
    let element;
    if (typeof children === "function") {
      element = children(fieldInfo);
    } else {
      element = children;
    }
    return Children.map(element, (child) =>
      isValidElement(child)
        ? cloneElement(child, { ...fieldInfo, name: field } as any)
        : child,
    );
  };

  const showError = !!errors[field] && !!touched[field];

  return (
    <Field name={field}>
      {({ field: fieldInfo }: FieldProps) => (
        <FormControl isInvalid={showError} isRequired={required}>
          <FormLabel mb="0" htmlFor={field}>
            {typeof label === "string" ? <Hint>{label}</Hint> : label}
          </FormLabel>
          {inputs(fieldInfo)}
          <Text
            fontSize="xs"
            visibility={showError ? "visible" : "hidden"}
            color="rosa.main"
          >
            {String(errors[field]) || "-"}
          </Text>
        </FormControl>
      )}
    </Field>
  );
}
