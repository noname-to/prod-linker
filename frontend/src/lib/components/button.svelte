<script lang="ts">
    import type { HTMLButtonAttributes } from "svelte/elements"
    import { cva, type VariantProps } from "$lib/cva.config"

    const button = cva({
        base: "rounded-md focus:outline-none focus-visible:ring text-base flex gap-2 items-center transition",
        variants: {
            intent: {
                primary: `bg-primary ring-yellow-400 hover:bg-yellow-400 disabled:bg-gray-200 \
                disabled:hover:bg-gray-200 disabled:text-gray-500`,
                secondary:
                    "text-blue-500 border border-neutral-200 ring-neutral-50 hover:bg-gray-100",
            },
            size: {
                small: "py-1 px-2",
                medium: "py-3 px-4",
            },
            busy: {
                true: "animate-pulse",
                false: "",
            },
        },
    })

    type $$Props = HTMLButtonAttributes & VariantProps<typeof button>
    let { class: className, ...rest } = $$restProps
    export let disabled: $$Props["disabled"] = false
    export let busy: $$Props["busy"] = false

    export let intent: $$Props["intent"] = "primary"
    export let size: $$Props["size"] = "medium"
</script>

<button class={button({ intent, size, busy, className })} {disabled} {...rest} on:click>
    <slot />
</button>
