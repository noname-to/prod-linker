<script lang="ts">
    import account from "$lib/assets/account.png"
    import acquiring from "$lib/assets/acquiring.png"
    import payment from "$lib/assets/payment.png"
    import { createUser } from "$lib/data/users"
    import { updateToken } from "$lib/data"
    import { goto } from "$app/navigation"

    const products = [
        { id: 1, name: "Расчётный счёт", image: account },
        { id: 3, name: "Касса", image: acquiring },
        { id: 2, name: "Интернет-эквайринг", image: payment },
    ]
</script>

<main class="flex flex-col w-full max-w-xl mx-auto py-4 sm:py-8 gap-2 max-sm:px-4">
    <div class="border border-gray-200 bg-gray-50 rounded-md py-2 px-4 mb-2">
        Выбор продукта сделан в демонстрационных целях.
    </div>
    <h2 class="text-sm font-medium text-gray-700">Заказать продукт</h2>
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {#each products as product}
            <button
                class="rounded bg-gray-50 px-4 pt-3 pb-0 flex flex-col justify-between hover:bg-gray-100 transition"
                on:click={async () => {
                    const res = await createUser(product.id)
                    updateToken(res.token)
                    await goto("/schedule")
                }}
            >
                <span class="font-medium mb-4">{product.name}</span>
                <img src={product.image} alt="" class="w-full object-cover" />
            </button>
        {/each}
    </div>
</main>
