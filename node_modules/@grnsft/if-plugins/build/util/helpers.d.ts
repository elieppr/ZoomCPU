import { ErrorFormatParams } from '../types/helpers';
/**
 * Formats given error according to class instance, scope and message.
 */
export declare const buildErrorMessage: (classInstanceName: string) => (params: ErrorFormatParams) => string;
