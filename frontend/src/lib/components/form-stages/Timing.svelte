<script lang="ts">
    import { cva } from "$lib/cva.config"
    import { format } from "date-fns"
    import { ru } from "date-fns/locale"
    import Carousel from "../carousel.svelte"
    import { availableTimeslots, selectedSlot, formStage } from "./store"

    import Button from "$lib/components/button.svelte"

    const chip = cva({
        base: "rounded-full py-2 px-3 transition min-w-fit",
        variants: {
            selected: {
                true: "bg-primary",
                false: "bg-gray-200 hover:bg-gray-300",
            },
        },
    })

    let selectedDay = 0
</script>

<h2 class="text-xl font-medium">Удобное время встречи</h2>

{#if $availableTimeslots === null}
    <div class="bg-neutral-200 animate-pulse rounded-md w-full h-16" />
{:else}
    <p class="mt-1 text-sm font-medium">День встречи</p>
    <Carousel>
        {#each $availableTimeslots as day, i (day.day)}
            <button
                class={chip({ selected: i === selectedDay })}
                on:click={() => {
                    selectedDay = i
                    selectedSlot.set(null)
                }}
            >
                {format(day.day, "dd MMMM", { locale: ru })}
            </button>
        {/each}
    </Carousel>
    <p class="mt-1 text-sm font-medium">Время встречи</p>
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {#each $availableTimeslots[selectedDay].slots as slot (slot)}
            <Button
                intent={$selectedSlot == slot ? "primary" : "secondary"}
                on:click={() => {
                    selectedSlot.set(slot)
                }}
                class="justify-center"
            >
                {format(slot, "HH:mm", { locale: ru })}
            </Button>
        {/each}
    </div>
    <div class="flex gap-2">
        <Button
            intent="secondary"
            class="justify-center flex-1"
            on:click={() => {
                formStage.set("address")
            }}
        >
            Назад
        </Button>
        <Button
            intent="primary"
            class="justify-center flex-1"
            disabled={!$selectedSlot}
            on:click={async () => {
                formStage.set("confidant")
            }}
        >
            Занять слот
        </Button>
    </div>
{/if}
