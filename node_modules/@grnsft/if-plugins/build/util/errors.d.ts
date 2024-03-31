declare const CUSTOM_ERRORS: readonly ["InputValidationError", "UnsupportedValueError", "ReadFileError", "WriteFileError", "MakeDirectoryError", "ConfigValidationError"];
type CustomErrors = {
    [K in (typeof CUSTOM_ERRORS)[number]]: ErrorConstructor;
};
export declare const ERRORS: CustomErrors;
export {};
