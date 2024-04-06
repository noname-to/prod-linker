<script lang="ts">
    import checkmark from "$lib/assets/checkmark.svg"
    import Button from "$lib/components/button.svelte"

    import { formStage } from "$lib/components/form-stages/store"
</script>

<div class="ready-container">
    <img class="w-24 h-24 mb-4 bg-primary rounded-full" src={checkmark} alt="Галочка" />
    <h2 class="text-2xl font-medium">Ваша заявка одобрена</h2>
    <p class="text-gray-600">Осталось встретиться с нашим представителем и подписать документы</p>
    <Button class="mt-3" on:click={() => formStage.set("address")}>Назначить встречу</Button>
</div>

<style>
    .ready-container {
        padding: 2rem;
        gap: 1rem;

        display: flex;
        align-items: center;
        flex-direction: column;

        text-align: center;
    }
</style>
