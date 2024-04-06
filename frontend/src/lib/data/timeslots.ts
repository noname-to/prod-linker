import { z } from "zod"
import type { AddressSuggestion } from "./addresses"
import { baseApiUrl, token } from "."

export const slotDay = z.object({
    day: z.coerce.date(),
    slots: z.array(z.coerce.date()),
})
export type SlotDay = z.infer<typeof slotDay>

export const timeslots = z.array(slotDay)
export type Timeslots = z.infer<typeof timeslots>

const timeslotsApiUrl = `${baseApiUrl}/meeting/meeting_slots`

export async function getAvailableMeetingTimeslots(address: AddressSuggestion) {
    const res = await fetch(timeslotsApiUrl, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": token(),
        },
        body: JSON.stringify({
            latitude: address.data.geo_lat,
            longitude: address.data.geo_lon,
        }),
    }).then((r) => r.json())

    return timeslots.parse(res)
}
