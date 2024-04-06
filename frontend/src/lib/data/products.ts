import { z } from "zod"

export const document = z.object({
    title: z.string(),
})

export const product = z.object({
    title: z.string(),
    documents: z.array(document),
    duration_minutes: z.number(),
    specialists: z.array(z.string()),
})
