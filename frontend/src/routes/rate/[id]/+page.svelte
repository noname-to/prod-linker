<script lang="ts">
    import { goto } from "$app/navigation"
    import Button from "$lib/components/button.svelte"
    import Input from "$lib/components/input.svelte"
    import { updateToken } from "$lib/data"
    import { leaveReview } from "$lib/data/review"
    import type { PageData } from "./$types"

    let comment = ""
    let rating = -1

    export let data: PageData
</script>

<main class="w-full max-w-lg mx-auto sm:rounded-lg bg-gray-50 p-4 sm:mt-4">
    <h1 class="text-lg font-medium mb-2">Оцените прошедшую встречу</h1>
    <div
        class="flex gap-2 items-center text-5xl sm:text-6xl text-primary mb-2 sm:mb-4 w-full
        overflow-x-auto overflow-y-hidden scrollable"
    >
        {#each [...Array(5)] as _, i}
            <button on:click={() => (rating = i)} class={rating < i ? "text-gray-300" : ""}>
                ★
            </button>
        {/each}
    </div>
    <Input placeholder="Комментарий" bind:value={comment} />
    <Button
        disabled={rating < 0}
        class="w-full justify-center mt-2"
        on:click={async () => {
            await leaveReview(data.id, rating + 1, comment)
            updateToken("")
            await goto("/")
            window.location.reload()
        }}
    >
        Отправить
    </Button>
</main>
