<script lang="ts">
    import type { HTMLInputAttributes } from "svelte/elements"

    type $$Props = Omit<HTMLInputAttributes, "type">
    export let checked: $$Props["checked"] = false
    let rest = $$restProps
</script>

<label class="cursor-pointer flex gap-2 items-center">
    <input type="radio" name="type" class="sr-only peer" {checked} {...rest} on:change />
    <div
        class="w-4 h-4 mb-0.5 inline-block rounded-full bg-gray-100 peer-checked:bg-gray-50 peer-checked:border-4 border-primary"
    />
    <slot />
</label>
