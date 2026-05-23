import { UploadApiOptions, v2 as Cloudinary } from 'cloudinary';
import type { Request } from 'express';
import type { StorageEngine } from 'multer';
declare type KnownKeys<T> = {
    [K in keyof T]: string extends K ? never : number extends K ? never : K;
} extends {
    [_ in keyof T]: infer U;
} ? U : never;
declare type File = Express.Multer.File;
declare type PickedUploadApiOptions = Pick<UploadApiOptions, KnownKeys<UploadApiOptions>>;
export declare type OptionCallback<T> = (req: Request, file: File) => Promise<T> | T;
declare type CloudinaryStorageUploadOptionsWithoutPublicId = {
    [key in keyof PickedUploadApiOptions]: OptionCallback<PickedUploadApiOptions[key]> | PickedUploadApiOptions[key];
};
declare type CloudinaryStorageUploadOptions = CloudinaryStorageUploadOptionsWithoutPublicId & {
    public_id?: OptionCallback<string>;
};
declare type Params = CloudinaryStorageUploadOptions | OptionCallback<PickedUploadApiOptions>;
export interface Options {
    cloudinary: typeof Cloudinary;
    params?: Params;
}
export declare class CloudinaryStorage implements StorageEngine {
    private cloudinary;
    private params;
    constructor(opts: Options);
    _handleFile(req: Request, file: File, callback: (error?: any, info?: Partial<File>) => void): Promise<void>;
    _removeFile(req: Request, file: File, callback: (error: Error) => void): void;
    private upload;
}
export declare function createCloudinaryStorage(opts: Options): CloudinaryStorage;
export default createCloudinaryStorage;
