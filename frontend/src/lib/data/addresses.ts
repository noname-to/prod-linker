import type { LngLat } from "@yandex/ymaps3-types"
import { z } from "zod"

const dadataApiToken = "6c5389dcb44aa113db4965e4848e1ceaebede545"

export const addressSuggestionData = z.object({
    country: z.string(),
    geo_lat: z.coerce.number(),
    geo_lon: z.coerce.number(),

    region_with_type: z.string().nullish(),
    region_type: z.string().nullish(),
    region_type_full: z.string().nullish(),
    region: z.string().nullish(),

    city_with_type: z.string().nullish(),
    city_type: z.string().nullish(),
    city_type_full: z.string().nullish(),
    city: z.string().nullish(),

    area_with_type: z.string().nullish(),
    area_type: z.string().nullish(),
    area_type_full: z.string().nullish(),
    area: z.string().nullish(),

    settlement_with_type: z.string().nullish(),
    settlement_type: z.string().nullish(),
    settlement_type_full: z.string().nullish(),
    settlement: z.string().nullish(),

    street_with_type: z.string().nullish(),
    street_type: z.string().nullish(),
    street_type_full: z.string().nullish(),
    street: z.string().nullish(),

    house_type: z.string().nullish(),
    house_type_full: z.string().nullish(),
    house: z.string().nullish(),

    block_type: z.string().nullish(),
    block_type_full: z.string().nullish(),
    block: z.string().nullish(),

    flat_type: z.string().nullish(),
    flat_type_full: z.string().nullish(),
    flat: z.string().nullish(),

    room_type: z.string().nullish(),
    room_type_full: z.string().nullish(),
    room: z.string().nullish(),
})

export const addressSuggestion = z.object({
    value: z.string(),
    unrestricted_value: z.string(),
    data: addressSuggestionData,
})
export type AddressSuggestion = z.infer<typeof addressSuggestion>

export const addressDetails = z.object({
    room: z.string().nullish(),
    entrance: z.string().nullish(),
    floor: z.string().nullish(),
    intercom: z.string().nullish(),
    comment: z.string().nullish(),
})
export type AddressDetails = z.infer<typeof addressDetails>

export const response = z.object({
    suggestions: z.array(addressSuggestion),
})

const suggestionsApiUrl = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
export async function getAddressSuggestions(query: string) {
    const res = await fetch(suggestionsApiUrl, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: "Token " + dadataApiToken,
        },
        body: JSON.stringify({
            query: query,
            count: 5,
            language: "ru",
            locations: [{ country: "Россия" }],
            locations_boost: [{ kladr_id: "77" }],
        }),
    }).then((r) => r.json())
    return response.parse(res).suggestions
}

const geolocatingApiUrl = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address"
export async function geolocatePoint(point: LngLat) {
    const res = await fetch(geolocatingApiUrl, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: "Token " + dadataApiToken,
        },
        body: JSON.stringify({
            lat: point[1],
            lon: point[0],
            count: 5,
            language: "ru",
        }),
    }).then((r) => r.json())
    return response.parse(res).suggestions
}
