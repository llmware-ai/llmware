import {Transform} from 'stream';


declare module 'cloudinary' {

    /****************************** Constants *************************************/
    /****************************** Transformations *******************************/
    type CropMode =
        | (string & {})
        | "scale"
        | "fit"
        | "limit"
        | "mfit"
        | "fill"
        | "lfill"
        | "pad"
        | "lpad"
        | "mpad"
        | "crop"
        | "thumb"
        | "imagga_crop"
        | "imagga_scale";
    type Gravity =
        | (string & {})
        | "north_west"
        | "north"
        | "north_east"
        | "west"
        | "center"
        | "east"
        | "south_west"
        | "south"
        | "south_east"
        | "xy_center"
        | "face"
        | "face:center"
        | "face:auto"
        | "faces"
        | "faces:center"
        | "faces:auto"
        | "body"
        | "body:face"
        | "adv_face"
        | "adv_faces"
        | "adv_eyes"
        | "custom"
        | "custom:face"
        | "custom:faces"
        | "custom:adv_face"
        | "custom:adv_faces"
        | "auto"
        | "auto:adv_face"
        | "auto:adv_faces"
        | "auto:adv_eyes"
        | "auto:body"
        | "auto:face"
        | "auto:faces"
        | "auto:custom_no_override"
        | "auto:none"
        | "liquid"
        | "ocr_text";
    type Angle =
        number
        | (string & {})
        | Array<number | string>
        | "auto_right"
        | "auto_left"
        | "ignore"
        | "vflip"
        | "hflip";
    type ImageEffect =
        | (string & {})
        | "hue"
        | "red"
        | "green"
        | "blue"
        | "negate"
        | "brightness"
        | "auto_brightness"
        | "brightness_hsb"
        | "sepia"
        | "grayscale"
        | "blackwhite"
        | "saturation"
        | "colorize"
        | "replace_color"
        | "simulate_colorblind"
        | "assist_colorblind"
        | "recolor"
        | "tint"
        | "contrast"
        | "auto_contrast"
        | "auto_color"
        | "vibrance"
        | "noise"
        | "ordered_dither"
        | "pixelate_faces"
        | "pixelate_region"
        | "pixelate"
        | "unsharp_mask"
        | "sharpen"
        | "blur_faces"
        | "blur_region"
        | "blur"
        | "tilt_shift"
        | "gradient_fade"
        | "vignette"
        | "anti_removal"
        | "overlay"
        | "mask"
        | "multiply"
        | "displace"
        | "shear"
        | "distort"
        | "trim"
        | "make_transparent"
        | "shadow"
        | "viesus_correct"
        | "fill_light"
        | "gamma"
        | "improve";

    type VideoEffect =
        (string & {})
        | "accelerate"
        | "reverse"
        | "boomerang"
        | "loop"
        | "make_transparent"
        | "transition";
    type AudioCodec = (string & {}) | "none" | "aac" | "vorbis" | "mp3";
    type AudioFrequency =
        string
        | (number & {})
        | 8000
        | 11025
        | 16000
        | 22050
        | 32000
        | 37800
        | 44056
        | 44100
        | 47250
        | 48000
        | 88200
        | 96000
        | 176400
        | 192000;
    /****************************** Flags *************************************/
    type ImageFlags =
        | (string & {})
        | Array<string>
        | "any_format"
        | "attachment"
        | "apng"
        | "awebp"
        | "clip"
        | "clip_evenodd"
        | "cutter"
        | "force_strip"
        | "getinfo"
        | "ignore_aspect_ratio"
        | "immutable_cache"
        | "keep_attribution"
        | "keep_iptc"
        | "layer_apply"
        | "lossy"
        | "preserve_transparency"
        | "png8"
        | "png32"
        | "progressive"
        | "rasterize"
        | "region_relative"
        | "relative"
        | "replace_image"
        | "sanitize"
        | "strip_profile"
        | "text_no_trim"
        | "no_overflow"
        | "text_disallow_overflow"
        | "tiff8_lzw"
        | "tiled";
    type VideoFlags =
        | (string & {})
        | Array<string>
        | "animated"
        | "awebp"
        | "attachment"
        | "streaming_attachment"
        | "hlsv3"
        | "keep_dar"
        | "splice"
        | "layer_apply"
        | "no_stream"
        | "mono"
        | "relative"
        | "truncate_ts"
        | "waveform";
    type ColorSpace = (string & {}) | "srgb" | "no_cmyk" | "keep_cmyk";
    type DeliveryType =
        | (string & {})
        | "upload"
        | "private"
        | "authenticated"
        | "fetch"
        | "multi"
        | "text"
        | "asset"
        | "list"
        | "facebook"
        | "twitter"
        | "twitter_name"
        | "instagram"
        | "gravatar"
        | "youtube"
        | "hulu"
        | "vimeo"
        | "animoto"
        | "worldstarhiphop"
        | "dailymotion";
    /****************************** URL *************************************/
    type ResourceType = (string & {}) | "image" | "raw" | "video";
    type ImageFormat =
        | (string & {})
        | "gif"
        | "png"
        | "jpg"
        | "bmp"
        | "ico"
        | "pdf"
        | "tiff"
        | "eps"
        | "jpc"
        | "jp2"
        | "psd"
        | "webp"
        | "zip"
        | "svg"
        | "webm"
        | "wdp"
        | "hpx"
        | "djvu"
        | "ai"
        | "flif"
        | "bpg"
        | "miff"
        | "tga"
        | "heic"
    type VideoFormat =
        | (string & {})
        | "auto"
        | "flv"
        | "m3u8"
        | "ts"
        | "mov"
        | "mkv"
        | "mp4"
        | "mpd"
        | "ogv"
        | "webm"

    export interface CommonTransformationOptions {
        transformation?: TransformationOptions;
        raw_transformation?: string;
        crop?: CropMode;
        width?: number | string;
        height?: number | string;
        size?: string;
        aspect_ratio?: number | string;
        gravity?: Gravity;
        x?: number | string;
        y?: number | string;
        zoom?: number | string;
        effect?: string | Array<number | string>;
        background?: string;
        angle?: Angle;
        radius?: number | string;
        overlay?: string | object; //might be Record<any, any>
        custom_function?: string | { function_type: (string & {}) | "wasm" | "remote", source: string }
        variables?: Array<string | object>; //might be Record<any, any>
        if?: string;
        else?: string;
        end_if?: string;
        dpr?: number | string;
        quality?: number | string;
        delay?: number | string;

        [futureKey: string]: any;
    }

    export interface ImageTransformationOptions extends CommonTransformationOptions {
        underlay?: string | Object; //might be Record<any, any>
        color?: string;
        color_space?: ColorSpace;
        opacity?: number | string;
        border?: string;
        default_image?: string;
        density?: number | string;
        format?: ImageFormat;
        fetch_format?: ImageFormat;
        effect?: string | Array<number | string> | ImageEffect;
        page?: number | string;
        flags?: ImageFlags | string;

        [futureKey: string]: any;
    }

    interface VideoTransformationOptions extends CommonTransformationOptions {
        audio_codec?: AudioCodec;
        audio_frequency?: AudioFrequency;
        video_codec?: string | Object; //might be Record<any, any>
        bit_rate?: number | string;
        fps?: string | Array<number | string>;
        keyframe_interval?: string;
        offset?: string,
        start_offset?: number | string;
        end_offset?: number | string;
        duration?: number | string;
        streaming_profile?: StreamingProfiles
        video_sampling?: number | string;
        format?: VideoFormat;
        fetch_format?: VideoFormat;
        effect?: string | Array<number | string> | VideoEffect;
        flags?: VideoFlags;

        [futureKey: string]: any;
    }

    interface TextStyleOptions {
        text_style?: string;
        font_family?: string;
        font_size?: number;
        font_color?: string;
        font_weight?: string;
        font_style?: string;
        background?: string;
        opacity?: number;
        text_decoration?: string
    }

    interface ConfigOptions {
        cloud_name?: string;
        api_key?: string;
        api_secret?: string;
        api_proxy?: string;
        private_cdn?: boolean;
        secure_distribution?: string;
        force_version?: boolean;
        ssl_detected?: boolean;
        secure?: boolean;
        cdn_subdomain?: boolean;
        secure_cdn_subdomain?: boolean;
        cname?: string;
        shorten?: boolean;
        sign_url?: boolean;
        long_url_signature?: boolean;
        use_root_path?: boolean;
        auth_token?: AuthTokenApiOptions;
        account_id?: string;
        provisioning_api_key?: string;
        provisioning_api_secret?: string;
        oauth_token?: string;

        [futureKey: string]: any;
    }

    export interface ResourceOptions {
        type?: string;
        resource_type?: string;
    }

    export interface UrlOptions extends ResourceOptions {
        version?: string;
        format?: string;
        url_suffix?: string;

        [futureKey: string]: any;
    }

    export interface ImageTagOptions {
        html_height?: string;
        html_width?: string;
        srcset?: object; //might be Record<any, any>
        attributes?: object; //might be Record<any, any>
        client_hints?: boolean;
        responsive?: boolean;
        hidpi?: boolean;
        responsive_placeholder?: boolean;

        [futureKey: string]: any;
    }

    export interface VideoTagOptions {
        source_types?: string | string[];
        source_transformation?: TransformationOptions;
        fallback_content?: string;
        poster?: string | object; //might be Record<any, any>
        controls?: boolean;
        preload?: string;

        [futureKey: string]: any;
    }

    /****************************** Admin API Options *************************************/
    export interface AdminApiOptions {
        agent?: object; //might be Record<any, any>
        content_type?: string;
        oauth_token?: string;

        [futureKey: string]: any;
    }

    export type VisualSearchParams = { image_url: string } | { image_asset_id: string } | { text: string };

    export interface ArchiveApiOptions {
        allow_missing?: boolean;
        async?: boolean;
        expires_at?: number;
        flatten_folders?: boolean;
        flatten_transformations?: boolean;
        keep_derived?: boolean;
        mode?: string;
        notification_url?: string;
        prefixes?: string;
        public_ids?: string[] | string;
        fully_qualified_public_ids?: string[] | string;
        skip_transformation_name?: boolean;
        tags?: string | string[];
        target_format?: TargetArchiveFormat;
        target_public_id?: string;
        target_tags?: string[];
        timestamp?: number;
        transformations?: TransformationOptions;
        type?: DeliveryType
        use_original_filename?: boolean;

        [futureKey: string]: any;
    }

    export interface UpdateApiOptions extends ResourceOptions {
        access_control?: string[];
        auto_tagging?: number;
        background_removal?: string;
        categorization?: string;
        context?: boolean | string;
        custom_coordinates?: string;
        detection?: string;
        face_coordinates?: string;
        headers?: string;
        notification_url?: string;
        ocr?: string;
        raw_convert?: string;
        similarity_search?: string;
        tags?: string | string[];
        moderation_status?: string;
        unsafe_update?: object; //might be Record<any, any>
        allowed_for_strict?: boolean;
        asset_folder?: string;
        unique_display_name?: boolean;
        display_name?: string

        [futureKey: string]: any;
    }

    export interface PublishApiOptions extends ResourceOptions {
        invalidate?: boolean;
        overwrite?: boolean;

        [futureKey: string]: any;
    }

    export interface ResourceApiOptions extends ResourceOptions {
        transformation?: TransformationOptions;
        transformations?: TransformationOptions;
        keep_original?: boolean;
        next_cursor?: boolean | string;
        public_ids?: string[];
        prefix?: string;
        all?: boolean;
        max_results?: number;
        tags?: boolean;
        tag?: string;
        context?: boolean;
        direction?: number | string;
        moderations?: boolean;
        start_at?: string;
        exif?: boolean;
        colors?: boolean;
        derived_next_cursor?: string;
        faces?: boolean;
        image_metadata?: boolean;
        media_metadata?: boolean;
        pages?: boolean;
        coordinates?: boolean;
        phash?: boolean;
        cinemagraph_analysis?: boolean;
        accessibility_analysis?: boolean;
        related?: boolean;

        [futureKey: string]: any;
    }

    export interface UploadApiOptions {
        access_mode?: AccessMode;
        allowed_formats?: Array<VideoFormat> | Array<ImageFormat>;
        async?: boolean;
        backup?: boolean;
        callback?: string;
        colors?: boolean;
        discard_original_filename?: boolean;
        eager?: TransformationOptions;
        eager_async?: boolean;
        eager_notification_url?: string;
        eval?: string;
        exif?: boolean;
        faces?: boolean;
        filename_override?: string;
        folder?: string;
        format?: VideoFormat | ImageFormat;
        image_metadata?: boolean;
        media_metadata?: boolean;
        invalidate?: boolean;
        moderation?: ModerationKind;
        notification_url?: string;
        overwrite?: boolean;
        phash?: boolean;
        proxy?: string;
        public_id?: string;
        quality_analysis?: boolean;
        resource_type?: "image" | "video" | "raw" | "auto";
        responsive_breakpoints?: Record<any, any>;
        return_delete_token?: boolean
        timestamp?: number;
        transformation?: TransformationOptions;
        type?: DeliveryType;
        unique_filename?: boolean;
        upload_preset?: string;
        use_filename?: boolean;
        chunk_size?: number;
        disable_promises?: boolean;
        oauth_token?: string;
        use_asset_folder_as_public_id_prefix?: boolean;

        [futureKey: string]: any;
    }

    export interface ProvisioningApiOptions {
        account_id?: string;
        provisioning_api_key?: string;
        provisioning_api_secret?: string;
        agent?: object; //might be Record<any, any>?
        content_type?: string;

        [futureKey: string]: any;
    }

    export interface AuthTokenApiOptions {
        key: string;
        acl: string;
        ip?: string;
        start_time?: number;
        duration?: number;
        expiration?: number;
        url?: string;
    }

    type TransformationOptions =
        string
        | string[]
        | VideoTransformationOptions
        | ImageTransformationOptions
        | Object //might be Record<any, any>
        | Array<ImageTransformationOptions>
        | Array<VideoTransformationOptions>;

    type ImageTransformationAndTagsOptions = ImageTransformationOptions | ImageTagOptions;
    type VideoTransformationAndTagsOptions = VideoTransformationOptions | VideoTagOptions;
    type ImageAndVideoFormatOptions = ImageFormat | VideoFormat;
    type ConfigAndUrlOptions = ConfigOptions | UrlOptions;
    type AdminAndPublishOptions = AdminApiOptions | PublishApiOptions;
    type AdminAndResourceOptions = AdminApiOptions | ResourceApiOptions;
    type AdminAndUpdateApiOptions = AdminApiOptions | UpdateApiOptions;

    /****************************** API *************************************/
    type Status = (string & {}) | "pending" | "approved" | "rejected";
    type StreamingProfiles =
        (string & {})
        | "4k"
        | "full_hd"
        | "hd"
        | "sd"
        | "full_hd_wifi"
        | "full_hd_lean"
        | "hd_lean";
    type ModerationKind = (string & {}) | "manual" | "webpurify" | "aws_rek" | "metascan";
    type AccessMode = (string & {}) | "public" | "authenticated";
    type TargetArchiveFormat = (string & {}) | "zip" | "tgz";

    // err is kept for backwards compatibility, it currently will always be undefined
    type ResponseCallback = (err?: any, callResult?: any) => any;

    type UploadResponseCallback = (err?: UploadApiErrorResponse, callResult?: UploadApiResponse) => void;

    export interface AdminApiPaginationResponse {
        next_cursor?: string;
    }

    export interface AdminApiBaseResponse {
        rate_limit_allowed?: number;
        rate_limit_reset_at?: string;
        rate_limit_remaining?: number;
    }

    export interface UploadApiResponse {
        public_id: string;
        version: number;
        signature: string;
        width: number;
        height: number;
        format: string;
        resource_type: "image" | "video" | "raw" | "auto";
        created_at: string;
        tags: Array<string>;
        pages: number;
        bytes: number;
        type: string;
        etag: string;
        placeholder: boolean;
        url: string;
        secure_url: string;
        access_mode: string;
        original_filename: string;
        moderation: Array<string>;
        access_control: Array<string>;
        context: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
        metadata: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
        colors?: [string, number][];

        [futureKey: string]: any;
    }

    export interface UploadApiErrorResponse {
        message: string;
        name: string;
        http_code: number;

        [futureKey: string]: any;
    }

    class UploadStream extends Transform {
    }

    export interface DeleteApiResponse {
        message: string;
        http_code: number;
    }

    export interface BaseAssetRelation {
        asset: string;
        status: 200;
    }

    export interface AssetRelationSuccess extends BaseAssetRelation {
        message: 'success';
        code: 'success_ids'
    }

    export interface AssetRelationAlreadyExists extends BaseAssetRelation {
        message: 'resource already exists';
        code: 'already_exists_ids';
    }

    export interface NewAssetRelationResponse {
        failed: [any],
        success: Array<AssetRelationSuccess | AssetRelationAlreadyExists>
    }

    export interface DeleteAssetRelation {
        failed: [any],
        success: Array<AssetRelationSuccess>
    }

    export interface MetadataFieldApiOptions {
        external_id?: string;
        type?: string;
        label?: string;
        mandatory?: boolean;
        default_value?: number;
        validation?: object; //there are 4 types, we need to discuss documentation team about it before implementing.
        datasource?: DatasourceEntry;

        [futureKey: string]: any;
    }

    export interface MetadataFieldApiResponse {
        external_id: string;
        type: string;
        label: string;
        mandatory: boolean;
        default_value: number;
        validation: object; //there are 4 types, we need to discuss documentation team about it before implementing.
        datasource: DatasourceEntry;

        [futureKey: string]: any;
    }

    export interface MetadataFieldsApiResponse extends AdminApiPaginationResponse, AdminApiBaseResponse  {
        metadata_fields: MetadataFieldApiResponse[]
    }

    export interface DatasourceChange {
        values: Array<DatasourceEntry>
    }

    export type MetadataRuleCondition =
        MetadataRulePopulatedCondition
        | MetadataRuleEqualsCondition
        | MetadataRuleIncludesCondition
        | MetadataRuleOrCondition
        | MetadataRuleAndCondition;

    export interface MetadataRulePopulatedCondition {
        metadata_field_id: string;
        populated: boolean;
    }

    export interface MetadataRuleEqualsCondition {
        metadata_field_id: string;
        equals: string;
    }

    export interface MetadataRuleIncludesCondition {
        metadata_field_id: string;
        includes: Array<string>;
    }

    export interface MetadataRuleOrCondition {
        and: Array<MetadataRuleCondition>
    }

    export interface MetadataRuleAndCondition {
        or: Array<MetadataRuleCondition>
    }

    export type MetadataRuleResult =
        MetadataRuleResultEnable
        | MetadataRuleResultEnableWithActivate
        | MetadataRuleResultEnableWithApply;

    interface MetadataRuleResultCommon {
        set_mandatory?: boolean;
    }

    export interface MetadataRuleResultEnable extends MetadataRuleResultCommon {
        enable: boolean;
    }

    export interface MetadataRuleResultEnableWithActivate extends MetadataRuleResultCommon {
        enable?: boolean;
        activate_values: "all" | {
            external_ids: string | Array<string> | null;
            mode?: "override" | "append";
        }
    }

    export interface MetadataRuleResultEnableWithApply extends MetadataRuleResultCommon {
        enable?: boolean;
        apply_value: {
            value: string | Array<string>;
            mode?: "default" | "append";
        }
    }

    export interface MetadataRule {
        metadata_field_id: string;
        name: string | null;
        condition: MetadataRuleCondition;
        result: MetadataRuleResult | Array<MetadataRuleResult>;
        state?: string;
    }

    export interface MetadataRuleResponse extends MetadataRule {
        condition_signature: string;
        external_id: string;
    }

    export type MetadataRulesListResponse = Array<MetadataRuleResponse>;

    export interface ResourceApiResponse extends AdminApiPaginationResponse, AdminApiBaseResponse {
        resources: [
            {
                public_id: string;
                format: string;
                version: number;
                resource_type: string;
                type: string;
                placeholder: boolean;
                created_at: string;
                bytes: number;
                width: number;
                height: number;
                backup: boolean;
                access_mode: string;
                url: string;
                secure_url: string;
                tags: Array<string>;
                context: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
                next_cursor: string;
                derived_next_cursor: string;
                exif: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
                image_metadata: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
                media_metadata: object;
                faces: number[][];
                quality_analysis: number;
                colors: [string, number][];
                derived: Array<string>;
                moderation: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
                phash: string;
                predominant: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
                coordinates: object; //won't change since it's response, we need to discuss documentation team about it before implementing.
                access_control: Array<string>;
                pages: number;

                [futureKey: string]: any;
            }
        ]
    }

    export type SignApiOptions = Record<string, any>;

    export interface DatasourceEntry {
        external_id?: string;
        value: string;
    }

    export namespace v2 {

        /****************************** Global Utils *************************************/

        function cloudinary_js_config(): string;

        function config(new_config?: boolean | ConfigOptions): ConfigOptions;

        function config<K extends keyof ConfigOptions, V extends ConfigOptions[K]>(key: K, value?: undefined): V;

        function config<K extends keyof ConfigOptions, V extends ConfigOptions[K]>(key: K, value: V): ConfigOptions & { [Property in K]: V }

        function url(public_id: string, options?: TransformationOptions | ConfigAndUrlOptions): string;

        /****************************** Tags *************************************/

        function image(source: string, options?: ImageTransformationAndTagsOptions | ConfigAndUrlOptions): string;

        function picture(public_id: string, options?: ImageTransformationAndTagsOptions | ConfigAndUrlOptions): string;

        function source(public_id: string, options?: TransformationOptions | ConfigAndUrlOptions): string;

        function video(public_id: string, options?: VideoTransformationAndTagsOptions | ConfigAndUrlOptions): string;

        /****************************** Utils *************************************/

        namespace utils {

            function sign_request(params_to_sign: SignApiOptions, options?: ConfigAndUrlOptions): {
                signature: string;
                api_key: string;
                [key: string]: any
            };

            function api_sign_request(params_to_sign: SignApiOptions, api_secret: string): string;

            function verifyNotificationSignature(body: string, timestamp: number, signature: string, valid_for?: number): boolean;

            function api_url(action?: string, options?: ConfigAndUrlOptions): string;

            function url(public_id?: string, options?: TransformationOptions | ConfigAndUrlOptions): string;

            function video_thumbnail_url(public_id?: string, options?: VideoTransformationOptions | ConfigAndUrlOptions): string;

            function video_url(public_id?: string, options?: VideoTransformationOptions | ConfigAndUrlOptions): string;

            function generate_transformation_string(options: TransformationOptions): string;

            function archive_params(options?: ArchiveApiOptions): Promise<any>;

            function download_archive_url(options?: ArchiveApiOptions | ConfigAndUrlOptions): string

            function download_zip_url(options?: ArchiveApiOptions | ConfigAndUrlOptions): string;

            function download_backedup_asset(asset_id?: string, version_id?: string, options?: ArchiveApiOptions | ConfigAndUrlOptions): string

            function generate_auth_token(options?: AuthTokenApiOptions): string;

            function webhook_signature(data?: string, timestamp?: number, options?: ConfigOptions): string;

            function private_download_url(publicID: string, format: string, options: Partial<{
                resource_type: ResourceType;
                type: DeliveryType;
                expires_at: number;
                attachment: boolean;
            }>): string;
        }

        /****************************** Admin API V2 Methods *************************************/

        namespace api {
            function create_streaming_profile(name: string, options: AdminApiOptions | {
                display_name?: string,
                representations: TransformationOptions
            }, callback?: ResponseCallback): Promise<any>;

            function create_transformation(name: string, transformation: TransformationOptions, callback?: ResponseCallback): Promise<any>;

            function create_transformation(name: string, transformation: TransformationOptions, options?: AdminApiOptions | {
                allowed_for_strict?: boolean
            }, callback?: ResponseCallback): Promise<any>;

            function create_upload_mapping(folder: string, options: AdminApiOptions | {
                template: string
            }, callback?: ResponseCallback): Promise<any>;

            function create_upload_preset(options?: AdminApiOptions | {
                name?: string,
                unsigned?: boolean,
                disallow_public_id?: boolean
            }, callback?: ResponseCallback): Promise<any>;

            function delete_all_resources(value?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<any>;

            function delete_derived_by_transformation(public_ids: string[], transformations: TransformationOptions, callback?: ResponseCallback): Promise<any>;

            function delete_derived_by_transformation(public_ids: string[], transformations: TransformationOptions, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function delete_derived_resources(public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function delete_derived_resources(public_ids: string[], options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<any>;

            function delete_resources(value: string[], callback?: ResponseCallback): Promise<any>;

            function delete_resources(value: string[], options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<any>;

            function delete_resources_by_prefix(prefix: string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<any>;

            function delete_resources_by_prefix(prefix: string, callback?: ResponseCallback): Promise<any>;

            function delete_resources_by_tag(tag: string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<any>;

            function delete_resources_by_tag(tag: string, callback?: ResponseCallback): Promise<any>;

            function delete_streaming_profile(name: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function delete_streaming_profile(name: string, callback?: ResponseCallback): Promise<any>;

            function delete_transformation(transformationName: TransformationOptions, callback?: ResponseCallback): Promise<any>;

            function delete_transformation(transformationName: TransformationOptions, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function delete_upload_mapping(folder: string, callback?: ResponseCallback): Promise<any>;

            function delete_upload_mapping(folder: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function delete_upload_preset(name: string, callback?: ResponseCallback): Promise<any>;

            function delete_upload_preset(name: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function get_streaming_profile(name: string | ResponseCallback, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function get_streaming_profile(name: string | ResponseCallback, callback?: ResponseCallback): Promise<any>;

            function list_streaming_profiles(callback?: ResponseCallback): Promise<any>;

            function list_streaming_profiles(options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function ping(options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function ping(callback?: ResponseCallback): Promise<any>;

            function publish_by_ids(public_ids: string[], options?: AdminAndPublishOptions, callback?: ResponseCallback): Promise<any>;

            function publish_by_ids(public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function publish_by_prefix(prefix: string[] | string, options?: AdminAndPublishOptions, callback?: ResponseCallback): Promise<any>;

            function publish_by_prefix(prefix: string[] | string, callback?: ResponseCallback): Promise<any>;

            function publish_by_tag(tag: string, options?: AdminAndPublishOptions, callback?: ResponseCallback): Promise<any>;

            function publish_by_tag(tag: string, callback?: ResponseCallback): Promise<any>;

            function resource(public_id: string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<any>;

            function resource(public_id: string, callback?: ResponseCallback): Promise<any>;

            function resource_types(options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function resources(options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<any>;

            function resources_by_context(key: string, value?: string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_context(key: string, value?: string, options?: AdminAndResourceOptions): Promise<ResourceApiResponse>;

            function resources_by_context(key: string, options?: AdminAndResourceOptions): Promise<ResourceApiResponse>;

            function resources_by_context(key: string, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_asset_ids(asset_ids: string[] | string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_asset_ids(asset_ids: string[] | string, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_ids(public_ids: string[] | string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_ids(public_ids: string[] | string, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_asset_folder(asset_folder: string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_asset_folder(asset_folder: string, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_moderation(moderation: ModerationKind, status: Status, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_moderation(moderation: ModerationKind, status: Status, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_tag(tag: string, options?: AdminAndResourceOptions, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function resources_by_tag(tag: string, callback?: ResponseCallback): Promise<ResourceApiResponse>;

            function restore(public_ids: string[], options?: AdminApiOptions | {
                resource_type: ResourceType,
                type: DeliveryType
            }, callback?: ResponseCallback): Promise<any>;

            function restore(public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function root_folders(callback?: ResponseCallback, options?: AdminApiOptions): Promise<any>;

            function search(params: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function search(params: string, callback?: ResponseCallback): Promise<any>;

            function sub_folders(root_folder: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function sub_folders(root_folder: string, callback?: ResponseCallback): Promise<any>;

            function search_folders(search_input: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function search_folders(search_input: string, callback?: ResponseCallback): Promise<any>;

            function visual_search(params: VisualSearchParams, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function visual_search(params: VisualSearchParams, callback?: ResponseCallback): Promise<any>;

            function tags(options?: AdminApiOptions | {
                max_results?: number,
                next_cursor?: string,
                prefix?: string
            }, callback?: ResponseCallback): Promise<any>;

            function transformation(transformation: TransformationOptions, options?: AdminApiOptions | {
                max_results?: number,
                next_cursor?: string,
                named?: boolean
            }, callback?: ResponseCallback): Promise<any>;

            function transformation(transformation: TransformationOptions, callback?: ResponseCallback): Promise<any>;

            function transformations(options?: AdminApiOptions | {
                max_results?: number,
                next_cursor?: string,
                named?: boolean
            }, callback?: ResponseCallback): Promise<any>;

            function transformations(callback?: ResponseCallback): Promise<any>;

            function update(public_id: string, options?: AdminAndUpdateApiOptions, callback?: ResponseCallback): Promise<any>;

            function update(public_id: string, callback?: ResponseCallback): Promise<any>;

            function update_resources_access_mode_by_ids(access_mode: AccessMode, ids: string[], options?: AdminAndUpdateApiOptions, callback?: ResponseCallback): Promise<any>;

            function update_resources_access_mode_by_ids(access_mode: AccessMode, ids: string[], callback?: ResponseCallback): Promise<any>;

            function update_resources_access_mode_by_prefix(access_mode: AccessMode, prefix: string, options?: AdminAndUpdateApiOptions, callback?: ResponseCallback): Promise<any>;

            function update_resources_access_mode_by_prefix(access_mode: AccessMode, prefix: string, callback?: ResponseCallback): Promise<any>;

            function update_resources_access_mode_by_tag(access_mode: AccessMode, tag: string, options?: AdminAndUpdateApiOptions, callback?: ResponseCallback): Promise<any>;

            function update_resources_access_mode_by_tag(access_mode: AccessMode, tag: string, callback?: ResponseCallback): Promise<any>;

            function update_streaming_profile(name: string, options: {
                display_name?: string,
                representations: Array<{ transformation?: VideoTransformationOptions }>
            }, callback?: ResponseCallback): Promise<any>;

            function update_transformation(transformation_name: TransformationOptions, updates?: TransformationOptions, callback?: ResponseCallback): Promise<any>;

            function update_transformation(transformation_name: TransformationOptions, callback?: ResponseCallback): Promise<any>;

            function update_upload_mapping(name: string, options: AdminApiOptions | {
                template: string
            }, callback?: ResponseCallback): Promise<any>;

            function update_upload_preset(name?: string, options?: AdminApiOptions | {
                unsigned?: boolean,
                disallow_public_id?: boolean
            }, callback?: ResponseCallback): Promise<any>;

            function update_upload_preset(name?: string, callback?: ResponseCallback): Promise<any>;

            function upload_mapping(name?: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function upload_mapping(name?: string, callback?: ResponseCallback): Promise<any>;

            function upload_mappings(options?: AdminApiOptions | {
                max_results?: number,
                next_cursor?: string
            }, callback?: ResponseCallback): Promise<any>;

            function upload_mappings(callback?: ResponseCallback): Promise<any>;

            function upload_preset(name?: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function upload_preset(name?: string, callback?: ResponseCallback): Promise<any>;

            function upload_presets(options?: AdminApiOptions | {
                max_results?: number,
                next_cursor?: string
            }, callback?: ResponseCallback): Promise<any>;

            function usage(callback?: ResponseCallback, options?: AdminApiOptions): Promise<any>;

            function usage(options?: AdminApiOptions): Promise<any>;

            function create_folder(path: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function delete_folder(path: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<any>;

            function add_related_assets(public_id: string, public_ids_to_relate: string | Array<string>, options?: AdminApiOptions, callback?: ResponseCallback): Promise<NewAssetRelationResponse>;

            function add_related_assets_by_asset_id(asset_id: string, public_ids_to_relate: string | Array<string>, options?: AdminApiOptions, callback?: ResponseCallback): Promise<NewAssetRelationResponse>;

            function delete_related_assets(public_id: string, public_ids_to_unrelate: string | Array<string>, options?: AdminApiOptions, callback?: ResponseCallback): Promise<DeleteAssetRelation>;

            function delete_related_assets_by_asset_id(asset_id: string, public_ids_to_unrelate: string | Array<string>, options?: AdminApiOptions, callback?: ResponseCallback): Promise<DeleteAssetRelation>;

            /****************************** Structured Metadata API V2 Methods *************************************/

            function add_metadata_field(field: MetadataFieldApiOptions, options?: AdminApiOptions, callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;

            function add_metadata_field(field: MetadataFieldApiOptions, callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;

            function list_metadata_fields(callback?: ResponseCallback, options?: AdminApiOptions): Promise<MetadataFieldsApiResponse>;

            function list_metadata_fields(options?: AdminApiOptions): Promise<MetadataFieldsApiResponse>;

            function delete_metadata_field(field_external_id: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<DeleteApiResponse>;

            function delete_metadata_field(field_external_id: string, callback?: ResponseCallback): Promise<DeleteApiResponse>;

            function metadata_field_by_field_id(external_id: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;

            function metadata_field_by_field_id(external_id: string, callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;

            function update_metadata_field(external_id: string, field: MetadataFieldApiOptions, options?: AdminApiOptions, callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;

            function update_metadata_field(external_id: string, field: MetadataFieldApiOptions, callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;

            function update_metadata_field_datasource(field_external_id: string, entries_external_id: DatasourceChange, options?: AdminApiOptions, callback?: ResponseCallback): Promise<DatasourceChange>;

            function update_metadata_field_datasource(field_external_id: string, entries_external_id: DatasourceChange, callback?: ResponseCallback): Promise<DatasourceChange>;

            function delete_datasource_entries(field_external_id: string, entries_external_id: string[], options?: AdminApiOptions, callback?: ResponseCallback): Promise<DatasourceChange>;

            function delete_datasource_entries(field_external_id: string, entries_external_id: string[], callback?: ResponseCallback): Promise<DatasourceChange>;

            function restore_metadata_field_datasource(field_external_id: string, entries_external_id: string[], options?: AdminApiOptions, callback?: ResponseCallback): Promise<DatasourceChange>;

            function restore_metadata_field_datasource(field_external_id: string, entries_external_id: string[], callback?: ResponseCallback): Promise<DatasourceChange>;

            /****************************** Structured Metadata Rules API V2 Methods *************************************/
            function add_metadata_rule(rule: MetadataRule, options?: AdminApiOptions, callback?: ResponseCallback): Promise<MetadataRuleResponse>;

            function add_metadata_rule(rule: MetadataRule, callback?: ResponseCallback): Promise<MetadataRuleResponse>;

            function list_metadata_rules(callback?: ResponseCallback, options?: AdminApiOptions): Promise<MetadataRulesListResponse>;

            function list_metadata_rules(options?: AdminApiOptions): Promise<MetadataRulesListResponse>;

            function update_metadata_rule(external_id: string, rule: MetadataRule, options?: AdminApiOptions, callback?: ResponseCallback): Promise<MetadataRuleResponse>;

            function update_metadata_rule(external_id: string, rule: MetadataRule, callback?: ResponseCallback): Promise<MetadataRuleResponse>;

            function delete_metadata_rule(external_id: string, options?: AdminApiOptions, callback?: ResponseCallback): Promise<DeleteApiResponse>;

            function delete_metadata_rule(external_id: string, callback?: ResponseCallback): Promise<DeleteApiResponse>;

        }

        /****************************** Upload API V2 Methods *************************************/

        namespace uploader {
            function add_context(context: string, public_ids: string[], options?: {
                type?: DeliveryType,
                resource_type?: ResourceType
            }, callback?: ResponseCallback): Promise<any>;

            function add_context(context: string, public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function add_tag(tag: string, public_ids: string[], options?: {
                type?: DeliveryType,
                resource_type?: ResourceType
            }, callback?: ResponseCallback): Promise<any>;

            function add_tag(tag: string, public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function create_archive(options?: ArchiveApiOptions, target_format?: TargetArchiveFormat, callback?: ResponseCallback,): Promise<any>;

            function create_zip(options?: ArchiveApiOptions, callback?: ResponseCallback): Promise<any>;

            function destroy(public_id: string, options?: {
                resource_type?: ResourceType,
                type?: DeliveryType,
                invalidate?: boolean
            }, callback?: ResponseCallback,): Promise<any>;

            function destroy(public_id: string, callback?: ResponseCallback,): Promise<any>;

            function explicit(public_id: string, options?: UploadApiOptions, callback?: ResponseCallback): Promise<any>;

            function explicit(public_id: string, callback?: ResponseCallback): Promise<any>;

            function explode(public_id: string, options?: {
                page?: 'all',
                type?: DeliveryType,
                format?: ImageAndVideoFormatOptions,
                notification_url?: string,
                transformations?: TransformationOptions
            }, callback?: ResponseCallback): Promise<any>

            function explode(public_id: string, callback?: ResponseCallback): Promise<any>

            function generate_sprite(tag: string, options?: {
                transformation?: TransformationOptions,
                format?: ImageAndVideoFormatOptions,
                notification_url?: string,
                async?: boolean
            }, callback?: ResponseCallback): Promise<any>;

            function generate_sprite(tag: string, callback?: ResponseCallback): Promise<any>;

            function image_upload_tag(field?: string, options?: UploadApiOptions): Promise<any>;

            function multi(tag: string, options?: {
                transformation?: TransformationOptions,
                async?: boolean,
                format?: ImageAndVideoFormatOptions,
                notification_url?: string
            }, callback?: ResponseCallback): Promise<any>;

            function multi(tag: string, callback?: ResponseCallback): Promise<any>;

            function remove_all_context(public_ids: string[], options?: {
                context?: string,
                resource_type?: ResourceType,
                type?: DeliveryType
            }, callback?: ResponseCallback): Promise<any>;

            function remove_all_context(public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function remove_all_tags(public_ids: string[], options?: {
                tag?: string,
                resource_type?: ResourceType,
                type?: DeliveryType
            }, callback?: ResponseCallback): Promise<any>;

            function remove_all_tags(public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function remove_tag(tag: string, public_ids: string[], options?: {
                tag?: string,
                resource_type?: ResourceType,
                type?: DeliveryType
            }, callback?: ResponseCallback): Promise<any>;

            function remove_tag(tag: string, public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function rename(from_public_id: string, to_public_id: string, options?: {
                resource_type?: ResourceType,
                type?: DeliveryType,
                to_type?: DeliveryType,
                overwrite?: boolean,
                invalidate?: boolean
            }, callback?: ResponseCallback): Promise<any>;

            function rename(from_public_id: string, to_public_id: string, callback?: ResponseCallback): Promise<any>;

            function replace_tag(tag: string, public_ids: string[], options?: {
                resource_type?: ResourceType,
                type?: DeliveryType
            }, callback?: ResponseCallback): Promise<any>;

            function replace_tag(tag: string, public_ids: string[], callback?: ResponseCallback): Promise<any>;

            function text(text: string, options?: TextStyleOptions | {
                public_id?: string
            }, callback?: ResponseCallback): Promise<any>;

            function text(text: string, callback?: ResponseCallback): Promise<any>;

            function unsigned_image_upload_tag(field: string, upload_preset: string, options?: UploadApiOptions): Promise<any>;

            function unsigned_upload(file: string, upload_preset: string, options?: UploadApiOptions, callback?: ResponseCallback): Promise<any>;

            function unsigned_upload(file: string, upload_preset: string, callback?: ResponseCallback): Promise<any>;

            function unsigned_upload_stream(upload_preset: string, options?: UploadApiOptions, callback?: ResponseCallback): UploadStream;

            function unsigned_upload_stream(upload_preset: string, callback?: ResponseCallback): UploadStream;

            function upload(file: string, options?: UploadApiOptions, callback?: UploadResponseCallback): Promise<UploadApiResponse>;

            function upload(file: string, callback?: UploadResponseCallback): Promise<UploadApiResponse>;

            function upload_chunked(path: string, options?: UploadApiOptions, callback?: UploadResponseCallback): Promise<UploadApiResponse>;

            function upload_chunked(path: string, callback?: UploadResponseCallback): Promise<UploadApiResponse>;

            function upload_chunked_stream(options?: UploadApiOptions, callback?: UploadResponseCallback): UploadStream;

            function upload_large(path: string, options?: UploadApiOptions, callback?: UploadResponseCallback): Promise<UploadApiResponse>;

            function upload_large(path: string, callback?: UploadResponseCallback): Promise<UploadApiResponse>;

            function upload_stream(options?: UploadApiOptions, callback?: UploadResponseCallback): UploadStream;

            function upload_stream(callback?: UploadResponseCallback): UploadStream;

            function upload_tag_params(options?: UploadApiOptions, callback?: UploadResponseCallback): Promise<any>;

            function upload_url(options?: ConfigOptions): Promise<any>;

            function create_slideshow(options?: ConfigOptions & {
                manifest_transformation?: TransformationOptions,
                manifest_json?: Record<string, any>
            }, callback?: UploadResponseCallback): Promise<any>;

            /****************************** Structured Metadata API V2 Methods *************************************/

            function update_metadata(metadata: string | Record<any, any>, public_ids: string[], options?: UploadApiOptions, callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;

            function update_metadata(metadata: string | Record<any, any>, public_ids: string[], callback?: ResponseCallback): Promise<MetadataFieldApiResponse>;
        }

        /****************************** Search API *************************************/

        class search {

            aggregate(value?: string): search;

            execute(): Promise<any>;

            expression(value?: string): search;

            max_results(value?: number): search;

            next_cursor(value?: string): search;

            sort_by(key: string, value: 'asc' | 'desc'): search;

            ttl(newTtl: number): search;

            to_query(value?: string): search;

            with_field(value?: string): search;

            to_url(newTtl?: number, next_cursor?: string, options?: ConfigOptions): string;

            static aggregate(args?: string): search;

            static expression(args?: string): search;

            static instance(args?: string): search;

            static max_results(args?: number): search;

            static next_cursor(args?: string): search;

            static sort_by(key: string, value: 'asc' | 'desc'): search;

            static ttl(newTtl: number): search;

            static with_field(args?: string): search;
        }

        /****************************** Provisioning API *************************************/

        namespace provisioning {
            namespace account {
                function sub_accounts(enabled: boolean, ids?: string[], prefix?: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function sub_account(subAccountId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function create_sub_account(name: string, cloudName: string, customAttributes?: Record<any, any>, enabled?: boolean, baseAccount?: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function delete_sub_account(subAccountId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function update_sub_account(subAccountId: string, name?: string, cloudName?: string, customAttributes?: Record<any, any>, enabled?: boolean, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function user(userId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function users(pending: boolean, userIds?: string[], prefix?: string, subAccountId?: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function create_user(name: string, email: string, role: string, subAccountIds?: string[], options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function update_user(userId: string, name?: string, email?: string, role?: string, subAccountIds?: string[], options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function delete_user(userId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function create_user_group(name: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function update_user_group(groupId: string, name: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function delete_user_group(groupId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function add_user_to_group(groupId: string, userId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function remove_user_from_group(groupId: string, userId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function user_group(groupId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function user_groups(options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;

                function user_group_users(groupId: string, options?: ProvisioningApiOptions, callback?: ResponseCallback): Promise<any>;
            }
        }
    }
}
