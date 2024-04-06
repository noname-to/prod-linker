import { z } from "zod"
import { baseApiUrl, token } from "."
import { type AddressDetails, type AddressSuggestion, addressDetails } from "./addresses"
import { product } from "./products"
import { user, type Confidant } from "./users"
import { format } from "date-fns"

export const createResponse = z.object({
    _id: z.string(),
    user: user,
    representative: z.object({
        id: z.string(),
        last_name: z.string(),
        first_name: z.string(),
        middle_name: z.string(),
        avatar_filepath: z.string().nullish(),
        is_car: z.boolean(),
        phone_number: z.string(),
        vehicle_registration: z.string(),
        kpi: z.number(),
    }),
    start_time: z.coerce.date(),
    meeting_location: z.object({
        latitude: z.number(),
        longitude: z.number(),
    }),
    status: z.literal("assigned"),
    meeting_location_details: addressDetails,
    product: product,
    comment: z.string(),
})
export type CreatedMeeting = z.infer<typeof createResponse>

const createMeetingApiUrl = `${baseApiUrl}/meeting/create_meeting`
export async function createMeeting(
    address: AddressSuggestion,
    { comment, ...addressDetails }: AddressDetails,
    slot: Date,
    confidant: Confidant,
) {
    const res = await fetch(createMeetingApiUrl, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": token(),
        },
        body: JSON.stringify({
            start_time: format(slot, "yyyy-MM-dd'T'HH:mm:ss"),
            meeting_location_latitude: address.data.geo_lat,
            meeting_location_longitude: address.data.geo_lon,
            meeting_location_details: addressDetails,
            comment,
            confidant,
        }),
    }).then((r) => r.json())
    return createResponse.parse(res)
}

const getMeetingApiUrl = `${baseApiUrl}/user/get_meeting`
export async function getExistingMeeting() {
    const res = await fetch(getMeetingApiUrl, {
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": token(),
        },
    }).then((r) => r.json())
    return createResponse.parse(res)
}

const editMeetingApiUrl = `${baseApiUrl}/meeting/edit_meeting`
export async function editMeeting(
    id: string,
    address: AddressSuggestion,
    { comment, ...addressDetails }: AddressDetails,
    slot: Date,
    confidant: Confidant,
) {
    const fullUrl = `${editMeetingApiUrl}/${id}`
    const res = await fetch(fullUrl, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": token(),
        },
        body: JSON.stringify({
            start_time: format(slot, "yyyy-MM-dd'T'HH:mm:ss"),
            meeting_location_latitude: address.data.geo_lat,
            meeting_location_longitude: address.data.geo_lon,
            meeting_location_details: addressDetails,
            comment,
            confidant,
        }),
    }).then((r) => r.json())
    return createResponse.parse(res)
}

const cancelMeetingApiUrl = `${baseApiUrl}/meeting/cancel_meeting`
export async function cancelMeeting(id: string) {
    const fullUrl = `${cancelMeetingApiUrl}/${id}`
    await fetch(fullUrl, {
        method: "DELETE",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": token(),
        },
    })
}

const finishMeetingApiUrl = `${baseApiUrl}/meeting/finish_meeting`
export async function finishMeeting(id: string) {
    const fullUrl = `${finishMeetingApiUrl}/${id}`
    await fetch(fullUrl, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": token(),
        },
    })
}
