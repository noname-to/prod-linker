<script lang="ts">
    import {
        createdMeeting,
        formStage,
        type FormStage,
        selectedSuggestion,
        selectedSuggestionDetails,
    } from "$lib/components/form-stages/store"

    import Ready from "$lib/components/form-stages/Ready.svelte"
    import Confidant from "$lib/components/form-stages/Confidant.svelte"
    import Address from "$lib/components/form-stages/Address.svelte"
    import Timing from "$lib/components/form-stages/Timing.svelte"
    import Done from "$lib/components/form-stages/Done.svelte"

    import { onMount, type ComponentType } from "svelte"
    import { getExistingUser, type User } from "$lib/data/users"
    import { getExistingMeeting } from "$lib/data/meetings"
    import { geolocatePoint } from "$lib/data/addresses"

    let user: User | null = null

    onMount(async () => {
        user = await getExistingUser()
        const meeting = await getExistingMeeting().catch(() => null)
        if (meeting != null) {
            createdMeeting.set(meeting)
            selectedSuggestion.set(
                (
                    await geolocatePoint([
                        meeting.meeting_location.longitude,
                        meeting.meeting_location.latitude,
                    ])
                )[0],
            )
            selectedSuggestionDetails.set(meeting.meeting_location_details)
            formStage.set("done")
        }
    })

    const stages: { [stage in FormStage]: ComponentType } = {
        ready: Ready,
        confidant: Confidant,
        address: Address,
        timing: Timing,
        done: Done,
    }
</script>

<main
    class="w-full max-w-lg overflow-x-hidden mx-auto sm:mt-4 md:mt-16 bg-gray-50 rounded-xl flex flex-col gap-3 p-4"
>
    <svelte:component this={stages[$formStage]} />
</main>
<aside class="w-full max-w-lg mx-auto mt-4 mb-16">
    {#if user == null}
        <div class="w-full h-8 bg-gray-100 animate-pulse rounded-md" />
    {:else}
        <p class="text-sm text-gray-500 text-center px-4">
            {user.title} <span class="font-serif">•</span> ИНН: {user.inn}
        </p>
    {/if}
</aside>
