<script lang="ts">
    import type { LngLat, YMap, YMapLocationRequest } from "@yandex/ymaps3-types"
    import type { YMapDefaultMarker } from "@yandex/ymaps3-types/packages/markers"
    import { onMount, createEventDispatcher } from "svelte"

    const dispath = createEventDispatcher<{
        update: LngLat
    }>()

    let mapContainer: HTMLDivElement
    let marker: YMapDefaultMarker
    let map: YMap

    export let lat = 55.75396
    export let lon = 37.620293
    export let zoom = 12
    export let draggable = true

    export async function updateMarker(coordinates: LngLat) {
        marker.update({ coordinates })
        map.update({ location: { center: coordinates, zoom: 16 } })
    }

    onMount(async () => {
        await ymaps3.ready

        const LOCATION: YMapLocationRequest = {
            center: [lon, lat],
            zoom,
        }

        const { YMap, YMapDefaultSchemeLayer, YMapListener, YMapDefaultFeaturesLayer } = ymaps3
        const { YMapDefaultMarker } = await ymaps3.import("@yandex/ymaps3-markers@0.0.1")

        map = new YMap(mapContainer, { location: LOCATION })
        map.addChild(new YMapDefaultSchemeLayer({}))
        map.addChild(new YMapDefaultFeaturesLayer({}))

        marker = new YMapDefaultMarker({
            coordinates: [lon, lat],
            draggable: false,
            color: "#FEDD2C",
        })

        map.addChild(marker)

        const listener = new YMapListener({
            layer: "any",
            onUpdate: (e) => {
                marker.update({
                    coordinates: e.location.center,
                })
                dispath("update", e.location.center)
            },
        })
        map.addChild(listener)

        if (!draggable) map.setBehaviors([])
    })
</script>

<div bind:this={mapContainer} class="h-64 rounded-md overflow-hidden"></div>
