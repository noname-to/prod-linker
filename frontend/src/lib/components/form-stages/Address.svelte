<script lang="ts">
    import {
        getAddressSuggestions,
        type AddressSuggestion,
        geolocatePoint,
    } from "$lib/data/addresses"
    import { isInDeliveryZone } from "$lib/geojson"
    import { debounce, suggestionToAddress } from "$lib/utils"
    import type { LngLat } from "@yandex/ymaps3-types"
    import { onMount } from "svelte"

    import Input from "$lib/components/input.svelte"
    import Map from "$lib/components/map.svelte"
    import Button from "$lib/components/button.svelte"

    import {
        availableTimeslots,
        formStage,
        selectedSuggestion,
        selectedSuggestionDetails,
        error,
    } from "$lib/components/form-stages/store"
    import { getExistingUser } from "$lib/data/users"

    let map: Map
    let suggestions: AddressSuggestion[] = []

    $: inBuilding = $selectedSuggestion?.data.house != null

    $: inDeliveryZone =
        $selectedSuggestion != null
            ? isInDeliveryZone([
                  $selectedSuggestion.data?.geo_lon,
                  $selectedSuggestion?.data.geo_lat,
              ])
            : false

    let ignoreUpdate = false

    let address = "" // адрес, до дома+корпуса
    let entrance = "" // подъезд
    let floor = "" // этаж
    let room = "" // квартира/комната/офис
    let intercom = "" // домофон
    let comment = ""

    let oldAddressSuggested = false
    let typingAddress = false

    onMount(async () => {
        const u = await getExistingUser()
        if (u?.last_known_location) {
            const mapSuggestions = await geolocatePoint([
                u.last_known_location.coordinates.longitude,
                u.last_known_location.coordinates.latitude,
            ])
            selectedSuggestion.set(mapSuggestions[0])
            selectedSuggestionDetails.set({
                ...u.last_known_location.address_details,
                comment: u.last_known_location.comment,
            })
            address = suggestionToAddress(mapSuggestions[0])
            oldAddressSuggested = true
        }

        const suggestion = $selectedSuggestion
        if (suggestion != null) {
            if (!address) address = suggestionToAddress(suggestion)

            setTimeout(() => {
                ignoreUpdate = true
                map.updateMarker([suggestion.data.geo_lon, suggestion.data.geo_lat])
            }, 250)
        }

        entrance = $selectedSuggestionDetails.entrance ?? ""
        floor = $selectedSuggestionDetails.floor ?? ""
        room = $selectedSuggestionDetails.room ?? ""
        intercom = $selectedSuggestionDetails.intercom ?? ""
        comment = $selectedSuggestionDetails.comment ?? ""
    })

    const applySuggestion = async (suggestion: AddressSuggestion) => {
        ignoreUpdate = true
        selectedSuggestion.set(suggestion)

        map.updateMarker([suggestion.data.geo_lon, suggestion.data.geo_lat])

        address = suggestionToAddress(suggestion)
        room = suggestion.data.flat ?? suggestion.data.room ?? ""
        floor = ""
        intercom = ""
        entrance = ""

        error.set(false)
    }

    const debouncedSuggestions = debounce(async (query: string) => {
        suggestions = await getAddressSuggestions(query)
    }, 350)

    const debouncedGeolocation = debounce(async (point: LngLat) => {
        const mapSuggestions = await geolocatePoint(point)

        address = suggestionToAddress(mapSuggestions[0])
        selectedSuggestion.set(mapSuggestions[0])
        suggestions = []
        error.set(false)

        room = ""
        floor = ""
        intercom = ""
        entrance = ""

        oldAddressSuggested = false
    }, 500)

    $: submitDisabled = !inDeliveryZone || !inBuilding || $error
</script>

<h2 class="text-xl font-medium">Место проведения встречи</h2>
<Map
    bind:this={map}
    on:update={(e) => {
        if (!ignoreUpdate) debouncedGeolocation(e.detail)
        ignoreUpdate = false
    }}
/>
<div class="flex flex-col gap-1">
    <Input
        bind:value={address}
        on:input={(e) => {
            selectedSuggestion.set(null)
            debouncedSuggestions(address)
            oldAddressSuggested = false
        }}
        on:suggested={(e) => {
            applySuggestion(e.detail)
        }}
        on:focus={() => (typingAddress = true)}
        on:blur={() => (typingAddress = false)}
        suggestions={suggestions.map((s) => ({ text: s.value, value: s }))}
        placeholder="Укажите ваш адрес или выберите его на карте"
    />
    {#if $selectedSuggestion !== null}
        {#if !inDeliveryZone}
            <p class="text-red-500 text-sm">К сожалению, пока что мы здесь не работаем :с</p>
        {:else if !inBuilding}
            <p class="text-red-500 text-sm">Заказать доставку можно только в помещение</p>
        {/if}
    {:else if !!address && !typingAddress}
        <p class="text-red-500 text-sm">Выберите адрес из списка</p>
    {/if}
    {#if oldAddressSuggested}
        <p class="text-sm">Подставили ваш старый адрес — проверяйте ;)</p>
    {/if}
</div>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
    <Input bind:value={entrance} placeholder="Подъезд" />
    <Input bind:value={room} placeholder="Квартира/офис" />
    <Input bind:value={floor} placeholder="Этаж" />
    <Input bind:value={intercom} placeholder="Домофон" />
</div>
<Input placeholder="Комментарий" bind:value={comment} />
<Button
    class="text-center justify-center"
    busy={!submitDisabled && $availableTimeslots === null}
    on:click={() => {
        selectedSuggestionDetails.set({
            floor,
            room,
            entrance,
            comment,
            intercom,
        })
        formStage.set("timing")
    }}
    disabled={submitDisabled || $availableTimeslots === null}
>
    Перейти к слотам
</Button>
{#if $error}
    <p class="text-red-500 text-sm">
        Не удалось получить доступные слоты, попробуйте другой адрес.
    </p>
{/if}
