import { apiSlice } from "./apiSlice";

export const analyzeApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    summarize: builder.mutation({
      query: (data) => ({
        url: "http://localhost:3000/api/v1/model",
        method: "POST",
        body: data,
      }),
    }),
    qna: builder.mutation({
      query: (data) => ({
        url: "http://localhost:3000/api/v1/qna",
        method: "POST",
        body: data,
      }),
    }),
  }),
});

export const { useSummarizeMutation, useQnaMutation } = analyzeApiSlice;
