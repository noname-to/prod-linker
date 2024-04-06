<script lang="ts">
    import Input from "$lib/components/input.svelte"
    import Button from "$lib/components/button.svelte"
    import Radio from "$lib/components/radio.svelte"
    import { createMeeting, editMeeting } from "$lib/data/meetings"
    import { onMount } from "svelte"
    import { getExistingUser } from "$lib/data/users"
    import {
        availableTimeslots,
        selectedSlot,
        formStage,
        selectedSuggestion,
        selectedSuggestionDetails,
        createdMeeting,
        error,
    } from "./store"

    let type = false
    const update = (e: Event) => {
        type = (e.target as HTMLInputElement).value === "true"
    }

    let firstName = ""
    let middleName = ""
    let lastName = ""

    let occupation = "" // должность
    let warrant = "" // доверенность

    let submitting = false

    onMount(async () => {
        const u = await getExistingUser()
        if (u?.default_confidant) {
            firstName = u.default_confidant.first_name
            lastName = u.default_confidant.last_name
            middleName = u.default_confidant.middle_name
            occupation = u.default_confidant.occupation ?? ""
            warrant = u.default_confidant.warrant ?? ""
            type = !!u.default_confidant.warrant
        }
    })
</script>

<h2 class="text-xl font-medium">Подписант договора</h2>

<div class="flex flex-col gap-1">
    <Radio value={false} checked={!type} on:change={update}>Сотрудник с правом подписи</Radio>
    <Radio value={true} checked={type} on:change={update}>Представитель по доверенности</Radio>
</div>

<Input placeholder="Фамилия" bind:value={lastName} />
<Input placeholder="Имя" bind:value={firstName} />
<Input placeholder="Отчество" bind:value={middleName} />
{#if !type}
    <Input placeholder="Наименование должности" bind:value={occupation} />
{:else}
    <Input placeholder="Сведения о доверенности" bind:value={warrant} />
{/if}
{#if $error}
    <p class="text-red-500 text-sm">Не удалось назначить встречу, попробуйте другой слот.</p>
{/if}
<Button
    class="justify-center"
    on:click={async () => {
        submitting = true
        const confidant = {
            first_name: firstName,
            last_name: lastName,
            middle_name: middleName,
            occupation,
            warrant,
        }
        const res = await (
            $createdMeeting
                ? editMeeting(
                      $createdMeeting._id,
                      // @ts-expect-error
                      $selectedSuggestion,
                      $selectedSuggestionDetails,
                      $selectedSlot,
                      confidant,
                  )
                : createMeeting(
                      // @ts-expect-error
                      $selectedSuggestion,
                      $selectedSuggestionDetails,
                      $selectedSlot,
                      confidant,
                  )
        ).catch((e) => {
            error.set(true)
            throw e
        })
        createdMeeting.set(res)
        formStage.set("done")
    }}
    disabled={submitting}
    busy={submitting}
>
    Назначить встречу
</Button>
