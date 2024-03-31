import { ZodSchema } from 'zod';
/**
 * At least one property defined handler.
 */
export declare const atLeastOneDefined: (obj: Record<string | number | symbol, unknown>) => boolean;
/**
 * All properties are defined handler.
 */
export declare const allDefined: (obj: Record<string | number | symbol, unknown>) => boolean;
/**
 * Validates given `object` with given `schema`.
 */
export declare const validate: <T>(schema: ZodSchema<T, import("zod").ZodTypeDef, T>, object: any) => T;
