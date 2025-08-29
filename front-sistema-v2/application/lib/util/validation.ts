import { onlyNumbers } from "./string";

export type RecordEntry = string | null | undefined;
export type ValidatorFn = (
  value?: string | null,
  data?: Record<string, RecordEntry>,
) => string | undefined;
export type OptionalValidation = (value?: string | null) => ValidatorFn[];
export type ObjectFromList<T extends ReadonlyArray<string>, V = string> = {
  [K in T extends ReadonlyArray<infer U> ? U : never]: V;
};

export const fieldValidators =
  <T>(ruleMap: Partial<Record<keyof T, ValidatorFn[] | OptionalValidation>>) =>
  (
    data: Record<keyof T, RecordEntry>,
  ): Partial<Record<keyof T, string | undefined>> => {
    const errors = {} as Record<keyof T, string | undefined>;
    for (const [field, rules] of Object.entries(ruleMap) as [
      keyof T,
      ValidatorFn[] | OptionalValidation,
    ][]) {
      let error: string | undefined;
      const value = data[field];
      const validators = typeof rules === "function" ? rules(value) : rules;
      for (const validator of validators) {
        error = validator(value, data);
        if (error) {
          errors[field] = error;
          break;
        }
      }
    }
    return errors;
  };

export const validYYYYMMDD: ValidatorFn = (dateStr?: string | null) =>
  isNaN(Number(new Date(dateStr + "T00:00:00"))) ? "Data inválida" : undefined;

export const optional =
  (...rules: ValidatorFn[]): OptionalValidation =>
  (value?: string | null) =>
    value ? rules : [];

export const required: ValidatorFn = (value?: string | null) => {
  if (!value?.trim().length) return "Campo obrigatório";
};

export const password: ValidatorFn = (value?: string | null) => {
  if (Number(value?.length) < 8)
    return "A senha precisa ter pelo menos 8 caracteres";
  if (!value?.match(/[0-9]/g)) return "A senha precisa de pelo menos 1 número";
  if (!value?.match(/[A-Z]/g))
    return "A senha precisa de pelo menos 1 letra maiúscula";
  if (!value?.match(/[a-z]/g))
    return "A senha precisa de pelo menos 1 letra minúscula";
};

export const cnpj: ValidatorFn = (value?: string | null) => {
  if (onlyNumbers(value ?? "").length !== 14) return "CNPJ inválido";
};

export const isin: ValidatorFn = (value?: string | null) => {
  if (value?.replace(/[^A-Z0-9]/g, "").length !== 12) return "ISIN inválido";
};

export const sameAs =
  (otherField: string, message: string): ValidatorFn =>
  (value?: string | null, data?: Record<string, RecordEntry>) => {
    if (data?.[otherField] !== value) return message;
  };

export const inList =
  (collection: Iterable<string>, message: string): ValidatorFn =>
  (value?: string | null) =>
    [...collection].includes(value ?? "") ? undefined : message;

export const unique =
  (set: Set<string | null>, message: string, exclude?: string): ValidatorFn =>
  (value?: string | null) =>
    set.has(value ?? null) ? message : undefined;

export const makeInitialValues = <Args extends string[]>(
  ...args: Args
): ObjectFromList<Args> =>
  args.reduce(
    (obj, arg) => ({ ...obj, [arg]: "" }),
    {} as ObjectFromList<Args>,
  );
