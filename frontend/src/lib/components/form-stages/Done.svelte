<script lang="ts">
    import { selectedSuggestion, selectedSlot, createdMeeting, formStage } from "./store"
    import { format } from "date-fns"
    import { ru } from "date-fns/locale"
    import Map from "$lib/components/map.svelte"
    import { baseApiUrl, updateToken } from "$lib/data"
    import Button from "../button.svelte"
    import { goto } from "$app/navigation"
    import { cancelMeeting, finishMeeting } from "$lib/data/meetings"
</script>

<h2 class="text-xl font-medium">Назначенная встреча</h2>

{#if $createdMeeting === null}
    <div
        class="border-4 border-transparent border-b-black animate-spin w-12 h-12 mx-auto rounded-full"
    />
{:else}
    <Map
        draggable={false}
        lat={$selectedSuggestion?.data.geo_lat}
        lon={$selectedSuggestion?.data.geo_lon}
        zoom={16}
    />
    <div class="flex flex-col gap-0.5">
        <h2 class="text-sm font-medium text-gray-700">Адрес</h2>
        <p class="text-xl">{$selectedSuggestion?.value}</p>
    </div>
    <div class="flex flex-col gap-0.5">
        <h2 class="text-sm font-medium text-gray-700">Дата и время</h2>
        <p class="text-xl">
            {format($createdMeeting.start_time, "d MMMM в HH:mm", { locale: ru })}
        </p>
    </div>
    <div class="flex flex-col gap-1.5">
        <h2 class="text-sm font-medium text-gray-700">Представитель</h2>
        <figure class="flex gap-2.5 items-center flex-wrap">
            <img
                class="rounded-md aspect-square w-12 object-cover"
                src="{baseApiUrl}/{$createdMeeting.representative.avatar_filepath}"
                alt="Портрет представителя"
            />
            <figcaption>
                <p class="text-xl">
                    {$createdMeeting.representative.first_name}
                    {$createdMeeting.representative.middle_name}
                    {$createdMeeting.representative.last_name}
                </p>
                <p class="text-sm text-gray-600">
                    {$createdMeeting.representative.phone_number}
                </p>
            </figcaption>
            <div class="flex-1" />
            <p class="text-xl font-semibold bg-white px-4 py-1 rounded border">
                {$createdMeeting.representative.vehicle_registration}
            </p>
        </figure>
    </div>
    <div class="flex flex-col gap-0.5">
        <h2 class="text-sm font-medium text-gray-700">Продукт</h2>
        <p class="text-xl">{$createdMeeting.product.title}</p>
    </div>
    <div class="flex flex-col gap-0.5">
        <h2 class="text-sm font-medium text-gray-700">Документы для встречи</h2>
        {#each $createdMeeting.product.documents as doc}
            <p class="text-xl"><span class="font-serif">•</span>&#160 {doc.title}</p>
        {/each}
    </div>
    <div class="flex flex-col gap-0.5">
        <h2 class="text-sm font-medium text-gray-700">Сотрудники для встречи</h2>
        {#each $createdMeeting.product.specialists as specialist}
            <p class="text-xl"><span class="font-serif">•</span>&#160 {specialist}</p>
        {/each}
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <Button
            intent="secondary"
            on:click={() => {
                formStage.set("address")
            }}
        >
            Перенести
        </Button>
        <Button
            intent="secondary"
            on:click={() => {
                // @ts-expect-error
                cancelMeeting($createdMeeting._id)
                goto("/").then(() => window.location.reload())
            }}
        >
            Отменить
        </Button>
        <Button
            intent="secondary"
            on:click={async () => {
                // @ts-expect-error
                const id = $createdMeeting._id
                await finishMeeting(id)
                goto(`/rate/${id}`).then(() => window.location.reload())
            }}
        >
            Завершить
        </Button>
    </div>
    <Button
        intent="secondary"
        on:click={() => {
            updateToken("")
            goto("/").then(() => window.location.reload())
        }}
    >
        Выйти
    </Button>
{/if}
