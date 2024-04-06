import { derived, writable } from "svelte/store"
import { type AddressDetails, type AddressSuggestion } from "$lib/data/addresses"
import { getAvailableMeetingTimeslots, type Timeslots } from "$lib/data/timeslots"
import type { CreatedMeeting } from "$lib/data/meetings"

export type FormStage = "ready" | "address" | "timing" | "done" | "confidant"
export const formStage = writable<FormStage>("ready")
export const error = writable<boolean>(false)

export const selectedSuggestion = writable<AddressSuggestion | null>(null)
export const selectedSuggestionDetails = writable<AddressDetails>({})

export const availableTimeslots = derived<typeof selectedSuggestion, Timeslots | null>(
    selectedSuggestion,
    ($s, set) => {
        set(null)
        if ($s !== null)
            getAvailableMeetingTimeslots($s).then(
                (r) => set(r),
                () => error.set(true),
            )
    },
    null,
)

export const selectedSlot = writable<Date | null>(null)
export const createdMeeting = writable<CreatedMeeting | null>(null)
