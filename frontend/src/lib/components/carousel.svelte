<script lang="ts">
    import { onMount } from "svelte"

    let container: HTMLDivElement
    let down = false

    onMount(() => {
        const mouseMove = (e: MouseEvent) => {
            if (!down) return
            container.scrollLeft -= e.movementX
        }

        const mouseUp = () => {
            down = false
            container.style.cursor = "grab"
        }

        window.addEventListener("mousemove", mouseMove)
        window.addEventListener("mouseup", mouseUp)

        return () => {
            window.removeEventListener("mousemove", mouseMove)
            window.removeEventListener("mouseup", mouseUp)
        }
    })
</script>

<div
    class="flex gap-2 w-full overflow-x-auto scrollable select-none cursor-grab pb-2"
    bind:this={container}
    role="section"
    on:mousedown={() => {
        down = true
        container.style.cursor = "grabbing"
    }}
>
    <slot />
</div>
