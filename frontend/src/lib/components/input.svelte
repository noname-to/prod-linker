<script lang="ts" generics="T">
    import type { HTMLInputAttributes } from "svelte/elements"
    import { cva, type VariantProps } from "$lib/cva.config"

    import { createEventDispatcher } from "svelte"

    const input = cva({
        base: "rounded focus:outline-none focus:ring-1 ring-black px-4 pb-1 pt-6 transition bg-gray-100 focus:bg-gray-50 w-full peer",
    })

    export let value = ""
    let inputElement: HTMLInputElement

    const dispatch = createEventDispatcher<{ suggested: T }>()

    type $$Props = Omit<HTMLInputAttributes, "type"> &
        VariantProps<typeof input> & { suggestions?: { text: string; value: T }[] }
    export let suggestions: $$Props["suggestions"] = undefined
    const { class: className, placeholder, ...rest } = $$restProps
</script>

<label class="relative group block">
    <input
        placeholder=" "
        class={input({ className })}
        bind:this={inputElement}
        bind:value
        {...rest}
        on:change
        on:input
        on:focus
        on:blur
        autocomplete="off"
        spellcheck="false"
        autocorrect="off"
    />
    <span
        class="absolute left-4 top-1/2 peer-placeholder-shown:-translate-y-1/2 -translate-y-full peer-focus:text-sm peer-focus:-translate-y-full
        transition-all text-sm text-gray-400 pointer-events-none peer-placeholder-shown:text-base"
    >
        {placeholder}
    </span>
    {#if suggestions !== undefined && suggestions.length > 0}
        <div
            class="absolute inset-x-0 top-full flex flex-col z-10 shadow-lg bg-white rounded-md border border-gray-300 max-h-48 overflow-y-auto
            scrollable py-2 transition group-focus-within:translate-y-2 translate-y-3.5 opacity-0 group-focus-within:opacity-100 pointer-events-none group-focus-within:pointer-events-auto"
        >
            {#each suggestions as suggestion}
                <button
                    class="p-3 text-left transition hover:bg-gray-100"
                    on:click={(e) => {
                        // @ts-expect-error
                        e.target.blur()
                        dispatch("suggested", suggestion.value)
                    }}
                >
                    {suggestion.text}
                </button>
            {/each}
        </div>
    {/if}
</label>
