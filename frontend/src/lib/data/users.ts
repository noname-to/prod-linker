import { z } from "zod"
import { product } from "./products"
import { baseApiUrl, token } from "."
import { addressDetails } from "./addresses"

export const confidant = z.object({
    last_name: z.string(),
    first_name: z.string(),
    middle_name: z.string(),
    warrant: z.string().nullish(),
    occupation: z.string().nullish(),
})
export type Confidant = z.infer<typeof confidant>

export const user = z.object({
    legal_form: z.boolean(),
    title: z.string(),
    last_name: z.string(),
    first_name: z.string(),
    middle_name: z.string(),
    inn: z.string().nullish(),
    kpp: z.string().nullish(),
    ogrn: z.number().nullish(),
    address: z.string().nullish(),
    requested_product: product,
    telegram_id: z.number(),
    last_known_location: z
        .object({
            coordinates: z.object({
                latitude: z.number(),
                longitude: z.number(),
            }),
            address_details: addressDetails,
            comment: z.string(),
        })
        .nullish(),
    default_confidant: confidant,
})
export type User = z.infer<typeof user>

export const userCreateResponse = z.object({
    token: z.string(),
    user,
})

const createUserApiUrl = `${baseApiUrl}/user/create_user`
export async function createUser(pathway: number) {
    const fullUrl = `${createUserApiUrl}/${pathway}`
    const res = await fetch(fullUrl).then((r) => r.json())
    return userCreateResponse.parse(res)
}

const getUserApiUrl = `${baseApiUrl}/user/get_info`
export async function getExistingUser() {
    const t = token()
    if (!t) return null
    const res = await fetch(getUserApiUrl, {
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": t,
        },
    }).then((r) => r.json())
    return user.parse(res)
}
